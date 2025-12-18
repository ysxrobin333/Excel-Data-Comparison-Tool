# Excel 数据比对工具 (Excel Data Comparison Tool)

这是一个基于 Python 和 Streamlit 开发的网页版工具，用于快速比对两组 Excel 数据。它能够自动通过精确匹配对齐数据行，识别差异，并保持原始数据的相对顺序。

## 主要功能

*   **便捷输入**: 直接从 Excel 复制数据并粘贴到工具中（支持单列或多列）。
*   **精确比对**: 基于整行内容进行精确匹配，自动对齐相同的数据。
*   **差异高亮**:
    *   **Match**: 数据完全一致。
    *   **Only in A**: 该数据仅在 A 组中存在（B 组对应位置留空）。
    *   **Only in B**: 该数据仅在 B 组中存在（A 组对应位置留空）。
    *   **Mismatch**: 对应位置的数据不匹配。
*   **Excel 导出**: 比对结果可以直接下载为 Excel 文件 (`.xlsx`)。

## 安装说明

1.  **环境要求**: 请确保您的电脑上安装了 Python 3.8 或以上版本。
2.  **安装依赖**:
    在项目目录下打开终端（Terminal 或 CMD），运行以下命令安装所需的库：

    ```bash
    pip install -r requirements.txt
    ```

    或者手动安装：
    ```bash
    pip install streamlit pandas openpyxl xlsxwriter
    ```

## 使用方法

1.  **启动工具**:
    在终端中运行以下命令启动程序：

    ```bash
    streamlit run app.py
    ```

2.  **操作步骤**:
    *   工具启动后会自动在浏览器中打开。
    *   **步骤 1**: 将 Excel 中需要比对的第一组数据（包含一列或多列）复制并粘贴到 **Data Set A** 文本框中。
    *   **步骤 2**: 将第二组数据复制并粘贴到 **Data Set B** 文本框中。
    *   **步骤 3**: 如果您的数据包含表头（标题行），请勾选 **"My data includes headers"**。
    *   **步骤 4**: 点击 **"Compare Data"** 按钮开始比对。
    *   **步骤 5**: 查看下方的比对结果预览，或点击 **"📥 Download Result as Excel"** 下载比对完成的表格文件。

## 文件结构

*   `app.py`: 主程序代码。
*   `test_alignment.py`: 用于验证比对逻辑的测试脚本。
*   `requirements.txt`: 项目依赖列表。
*   `README.md`: 项目说明文档。
