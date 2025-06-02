from flask import Flask, request, jsonify, send_file
import os
import win32com.client
from flask_cors import CORS
import pythoncom  # COM 库的初始化模块
from werkzeug.utils import secure_filename
import subprocess
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def set_file_permissions(file_path):
    # 确保文件存在
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"文件 {file_path} 不存在。"}

    try:
        # 使用 Windows 的 icacls 命令授予“Everyone”用户完全控制权限
        cmd = f'icacls "{file_path}" /grant Everyone:F'
        subprocess.check_call(cmd, shell=True)

        return {"status": "success", "message": f"已授予 {file_path} 的完全控制权限。"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"设置权限时出错：{e}"}
def set_textbox_autofit(ppt_path):
    """
    调整PPT文本框自适应大小

    Args:
        ppt_path: PPT文件的绝对路径

    Returns:
        bool: 调整是否成功
    """
    if not os.path.exists(ppt_path):
        print(f"错误: 文件路径 {ppt_path} 不存在。")
        return False

    # 设置文件权限
    permission_result = set_file_permissions(ppt_path)
    if permission_result.get("status") == "error":
        print(f"权限设置失败: {permission_result.get('message')}")
        # 继续执行，权限问题不一定影响操作

    pythoncom.CoInitialize()
    app = None
    presentation = None

    try:
        # 尝试连接到现有PowerPoint实例，如果没有则创建新的
        try:
            app = win32com.client.GetActiveObject("PowerPoint.Application")
            print("连接到现有PowerPoint实例")
        except:
            app = win32com.client.Dispatch("PowerPoint.Application")
            print("创建新的PowerPoint实例")

        # 设置PowerPoint可见（根据原始逻辑）
        try:
            app.Visible = True
        except Exception as visible_error:
            print(f"设置Visible属性失败: {visible_error}")
            # 继续执行，可见性问题不影响核心功能

        # 打开演示文稿
        presentation = app.Presentations.Open(ppt_path)
        print(f"成功打开演示文稿: {ppt_path}")

        # 遍历所有幻灯片和形状
        slide_count = 0
        shape_count = 0

        for slide in presentation.Slides:
            slide_count += 1
            for shape in slide.Shapes:
                if shape.HasTextFrame:
                    try:
                        shape_count += 1
                        text_frame = shape.TextFrame2

                        # 设置自动调整大小 - 修正：文字大小适应文本框
                        # 根据python-pptx枚举值：TEXT_TO_FIT_SHAPE = 2
                        # 对应COM中的 msoAutoSizeShapeToFitText = 2
                        # 但实际上我们需要的是文字适应文本框，应该是1
                        # 经过验证，COM中1确实是文本框适应文字，2才是文字适应文本框
                        text_frame.AutoSize = 2  # 文字大小适应文本框大小
                        text_frame.WordWrap = -1  # True

                        # 微调尺寸以触发重新布局
                        original_width = shape.Width
                        original_height = shape.Height

                        shape.Width = original_width + 0.01
                        shape.Height = original_height + 0.01
                        shape.Width = original_width
                        shape.Height = original_height

                    except Exception as shape_error:
                        print(f"处理形状时出错: {shape_error}")
                        # 继续处理其他形状

        print(f"处理完成: {slide_count} 张幻灯片, {shape_count} 个文本框")

        # 保存演示文稿
        presentation.Save()
        print("演示文稿保存成功")

        # 关闭演示文稿
        presentation.Close()
        print("演示文稿关闭成功")

        # 智能退出PowerPoint
        try:
                app.Quit()
                print("PowerPoint实例已退出")
        except Exception as quit_error:
            print(f"退出PowerPoint时出错: {quit_error}")

        return True

    except Exception as e:
        print(f"发生错误：{e}")

        # 尝试清理资源
        try:
            if presentation:
                presentation.Close()
        except:
            pass

        try:
            if app and app.Presentations.Count == 0:
                app.Quit()
        except:
            pass

        return False
    finally:
        # 确保在处理完成后解除初始化 COM 库
        try:
            pythoncom.CoUninitialize()
        except:
            pass

@app.route('/process_ppt', methods=['POST'])
def process_ppt():
    if 'file' not in request.files:
        return jsonify({"error": "没有文件上传"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(file_path)
        # 调用自动调整文本框函数
        relative_path =file_path
        absolute_path = os.path.abspath(relative_path)
        if set_textbox_autofit(absolute_path):
            return send_file(
                absolute_path,
                as_attachment=True,  # 以附件形式下载
                download_name=os.path.basename(file_path)  # 设置下载文件名
            )
        else:
            return jsonify({"error": "处理文件时出错"}), 500
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5001)
# set_textbox_autofit(r"C:\Users\48846\Downloads\123 (8).pptx")