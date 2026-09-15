import re
import json
import traceback
import math
from react_agent.LLM import RequestLLM


class ReactAgent:

    def __init__(self, model: RequestLLM) -> None:
        # 提示词
        self.FN_NAME = '✿FUNCTION✿'
        self.FN_ARGS = '✿ARGS✿'
        self.FN_RESULT = '✿RESULT✿'
        self.FN_EXIT = '✿RETURN✿'
        self.FN_STOP_WORDS = [
            self.FN_RESULT,
            self.FN_RESULT + ':',
            self.FN_RESULT + ':\n',
        ]

        self.functions = {}
        self.last_parse_error = None
        self.FN_CALL_TEMPLATE_ZH = """
        # 你是我的机械臂助手，帮我控制一个六关节机械臂。机械臂内置了一些函数，请你根据我的指令和下面要求，输出对应需要执行的函数。
        ## 你拥有如下工具：
        {tool_descs}
        ## move_to用于将物体放到指定位置形成特定图案，show_object用于展示物体，grab_object用于寻找并抓取指定物体。必须首先使用grab_object工具，接着必须紧跟move_to或show_object工具。
        ## 所有工具一次都只能处理一个物体，因此当需要处理多个物体时，需要重复grab_object和move_to或show_object！
        ## 你可以在回复中插入零次、一次或多次以下命令以调用工具,最后恢复初始位置。如果需要循环，你可以多次调用同一工具；如果命令中需要实现多个功能，你也可以按顺序调用多个工具。工具函数出现的先后顺序，表示执行的先后顺序。
        ## 只允许输出实际要执行的FUNCTION和ARGS，不要复述规则、示例、占位符或分析过程。每个FUNCTION必须有且只有一个对应的ARGS。
        ## 这里有一些例子：
            一：我的指令：“抓取两个红色方块,一个展示给我，一个放到任意位置”。
            你输出：“
✿FUNCTION✿: grab_object
✿FUNCTION✿: show_object
✿FUNCTION✿: grab_object
✿FUNCTION✿: move_to
✿ARGS✿: {{"object_name": "红色方块"}}
✿ARGS✿: {{"object_name": "红色方块"}}
✿ARGS✿: {{"object_name": "红色方块"}}
✿ARGS✿: {{"target_coord": [-80,200]}}
”；因为我需要两个红色方块，所以你需要连续执行grab_object两次，第一次用show_object展示给我，第二次用Move_to移动到指定位置。其他指令的逻辑也类似。
二：我的指令：“用八个方块组成一个圆形,用代码计算精确坐标”。
这里,指令中明确要求了指定的图形，并且要求用代码计算坐标。因此首先你需要编写一段完整的python代码，需要可以直接运行并返回坐标结果，根据指令中要求的图案，计算出精确的各个点的坐标。所有点的X坐标范围是-70至140，Y坐标范围是150到280，"相邻两点之间的距离不小于50"，绝对不可以超出范围！要求结果必须存在全局变量global Result中！然后等待我帮你执行代码获取结果，接着根据我给你的结果给出工具参数。
        #只需要在指令中明确要求编写代码时，再使用代码计算坐标！代码要放到字符串“```python”和“```”中间以方便提取。
        %s: 工具名称，如果使用工具则必须是[{tool_names}]之一，工具的名称不得修改或翻译！
        %s: 工具输入，json格式输入！
        %s: 工具结果。
        %s: 根据工具结果必须使用用户问题的语种(汉语或其他语言)进行回复""" % (
            self.FN_NAME,
            self.FN_ARGS,
            self.FN_RESULT,
            self.FN_EXIT,
        )

        self.tool_descs_template = (
            '{func_name}: {description_for_func} 输入参数：{parameters}'
        )
        self.model = model

    # 注册工具
    def register_tool(self, name, cls):
        self.functions[name] = {
            'function': cls().call,
            'description': cls.description,
            'parameters': cls.parameters,
        }

    # 更新sys_message
    def update_system_message(self):
        tool_descs = '\n'.join([
            self.tool_descs_template.format(
                func_name=name,
                description_for_func=tool['description'],
                parameters=json.dumps(
                    tool['parameters'],
                    ensure_ascii=False,
                ),
            )
            for name, tool in self.functions.items()
        ])
        tool_names = ', '.join(self.functions.keys())
        self.model.messages = [
            {
                'role': 'system',
                'content': self.FN_CALL_TEMPLATE_ZH.format(
                    tool_descs=tool_descs,
                    tool_names=tool_names,
                ),
            }
        ]

    # 移除特殊字符
    def remove_special_tokens(self, text, strip=True):
        text = text.replace('✿:', '✿')
        text = text.replace('✿：', '✿')
        out = ''
        is_special = False
        for c in text:
            if c == '✿':
                is_special = not is_special
                continue
            if is_special:
                continue
            out += c
        if strip:
            out = out.lstrip('\n').rstrip()
        return out

    def extract_functions_and_args(self, input_str):
        """
        在执行任何工具前，完整解析并校验本轮的所有调用。

        机械臂场景采用安全失败：只要有一项不合法，整批都不执行。
        """
        self.last_parse_error = None

        function_matches = re.findall(
            r'✿FUNCTION✿:\s*(\w+)',
            input_str,
        )
        args_matches = re.findall(
            r'✿ARGS✿:\s*(\{.*?\})',
            input_str,
            re.DOTALL,
        )

        if len(function_matches) != len(args_matches):
            self.last_parse_error = (
                "模型输出格式错误：FUNCTION 数量为 {}，ARGS 数量为 {}。"
                "为避免机械臂误动作，本轮不执行任何工具。"
            ).format(len(function_matches), len(args_matches))
            return []

        result = []
        for function_name, args_str in zip(
            function_matches,
            args_matches,
        ):
            if function_name not in self.functions:
                self.last_parse_error = (
                    "模型输出了未知工具 '{}'。"
                    "为避免机械臂误动作，本轮不执行任何工具。"
                ).format(function_name)
                return []

            try:
                args_dict = json.loads(args_str)
            except json.JSONDecodeError as exc:
                self.last_parse_error = (
                    "工具 '{}' 的参数不是合法 JSON：{}。"
                    "为避免机械臂误动作，本轮不执行任何工具。"
                ).format(function_name, exc)
                return []

            if not isinstance(args_dict, dict):
                self.last_parse_error = (
                    "工具 '{}' 的参数必须是 JSON 对象。"
                    "为避免机械臂误动作，本轮不执行任何工具。"
                ).format(function_name)
                return []

            result.append((function_name, args_dict))

        return result

    def stream_output(self, response):
        for chunk in response:
            print(chunk, flush=True, end='')
        print()

    def extract_code(self, generated_content: str):
        code_match = re.search(
            r"```python\s*(.*?)```",
            generated_content,
            re.DOTALL,
        )
        if code_match:
            print("%%%%%%%%%")
            print(code_match)
            print("%%%%%%%%%")
            return code_match.group(1).strip()
        return None

    def run_code_and_format_result(self, code: str):
        try:
            exec(code)
            execution_result = globals().get('Result', None)
            print("&&&&&&&&&&&&")
            print(execution_result)
            print("&&&&&&&&&&&&")
            if execution_result is not None:
                return json.dumps({"result": execution_result})
            return "Execution succeeded, but no result variable was found."
        except Exception as exc:
            error_result = json.dumps({
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })
            print("&&&&&&&&&&&&")
            print(error_result)
            print("&&&&&&&&&&&&")
            return error_result

    # 对话
    def chat(self, prompt):
        response = self.model.chat_nostream(
            prompt=prompt,
            stop=self.FN_STOP_WORDS,
        )

        code_to_run = self.extract_code(
            self.model.messages[-1]['content']
        )

        if code_to_run:
            while True:
                execution_result = self.run_code_and_format_result(
                    code_to_run
                )

                if "error" not in execution_result:
                    break

                response = self.model.chat_nostream(
                    prompt=execution_result
                )
                code_to_run = self.extract_code(response)

            response = self.model.chat_nostream(
                prompt=execution_result
            )

        print('<LLM>:', end='')
        self.stream_output(response)

        assistant_content = self.model.messages[-1]['content']
        functions_and_args = self.extract_functions_and_args(
            assistant_content
        )

        print('functions_and_args:', functions_and_args)

        if self.last_parse_error:
            print(self.last_parse_error)
            return

        for fn_name, fn_args in functions_and_args:
            print("#" * 20, "<函数执行>", "#" * 20)
            res_func = self.functions[fn_name]['function'](**fn_args)
            print("#" * 20, "<函数执行>", "#" * 20, '\n')

            if (
                isinstance(res_func, dict)
                and res_func.get("success") is False
            ):
                print(
                    "工具执行失败，停止后续工具调用: {}".format(
                        res_func.get("error", res_func)
                    )
                )
                break
