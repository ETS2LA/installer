## 🛠️ **Standalone Tkinter for Embedded Python** 🛠️

This repository provides a straightforward way to install Tkinter into your Python embedded distribution. By following the instructions here, you can quickly set up Tkinter in your Python environment, ensuring you have all the necessary files and configurations to start building your desktop applications.

**Why Use This Repository?**

*   **Embed Tkinter**: This repository includes the required Tkinter files and configurations for different Python versions, tailored specifically for embedded Python distributions.
*   **Easy Integration**: Follow our easy drag-and-drop instructions to integrate Tkinter into your Python setup.
*   **Version-Specific**: We provide support for Python versions 3.10, 3.11, and 3.12, ensuring compatibility with your specific environment.
---

### 🚀 **Getting Started**


### 🐍 **For Python 3.10**

1.  **Download the Zip File from [**HERE**](https://github.com/ChrisColeTech/tkinter-standalone/releases/download/1.0.0/tkinter-standalone.zip)**: Unzip the provided archive to reveal the `tkinter` directory.
2.  **Navigate to**: `tkinter/3.10/python_embedded`
3.  **Move Files**: Drag and drop the files from `python_embedded` to your embedded Python directory.
4.  **Verify Structure**:  After moving the files, your folder structure should resemble this:

    <img src ="https://github.com/user-attachments/assets/b15bdbdb-c44d-439a-880b-849dde7c1493" height="300px">

    **Ensure**:
    
    *   `tcl` folder is at the root of the embedded distribution.
    *   `tkinter` folder is at the root of the embedded distribution.
    *   `_tkinter.pyd`, `tcl86t.dll`, and `tk86t.dll` are in the `DLLs` folder.
    *   **IMPORTANT:** Either replace `python310._pth` with the one provided in the Zip or edit your current `python310._pth` to include `./DLLs`.
5.  **Test Tkinter**: Run the following command to confirm Tkinter is set up correctly:
    
    `python -m tkinter`
    

  <img src ="https://github.com/user-attachments/assets/3cf43f13-f6d0-47c7-97a1-ef7f9116932b" height="300px">

  
---

### 🐍 **For Python 3.11**

1.  **Download the Zip File from [**HERE**](https://github.com/ChrisColeTech/tkinter-standalone/releases/download/1.0.0/tkinter-standalone.zip)**: Unzip the provided archive to reveal the `tkinter` directory.
2.  **Navigate to**: `tkinter/3.11/python_embedded`
3.  **Move Files**: Drag and drop the files from `python_embedded` to your embedded Python directory.
4.  **Verify Structure**:  After moving the files, your folder structure should resemble  this:

    <img src ="https://github.com/user-attachments/assets/1f321a89-46ba-48e4-9865-21b98472912f" height="300px">
    

    * **FOR 3.11 ONLY**:
    The tkinter folder should be at `\Lib\site-packages\tkinter`
    <img src ="https://github.com/user-attachments/assets/daa1e63d-0d7c-4d5f-a8d9-5eb115991f5f" height="100px">

    **Ensure**:
    
    *   `tcl` folder is at the root of the embedded distribution.
    *   `tkinter` folder is located at `\Lib\site-packages\tkinter`.
    *   `_tkinter.pyd`, `tcl86t.dll`, and `tk86t.dll` are in the `DLLs` folder.
    *    **IMPORTANT:** Either replace `python311._pth` with the one provided or edit your current `python311._pth` to include `./DLLs`.
6.  **Test Tkinter**: Execute this command to verify installation:
    
    `python -m tkinter`
   <img src ="https://github.com/user-attachments/assets/2f9d4a0f-3f12-4049-bcbc-01cbd1e66de7" height="300px">    


---

### 🐍 **For Python 3.12**

1.  **Download the Zip File from [**HERE**](https://github.com/ChrisColeTech/tkinter-standalone/releases/download/1.0.0/tkinter-standalone.zip)**: Unzip the provided archive to reveal the `tkinter` directory.
2.  **Navigate to**: `tkinter/3.12/python_embedded`
3.  **Move Files**: Drag and drop the files from `python_embedded` to your embedded Python directory.
4.  **Verify Structure**: After moving the files, your folder structure should resemble this:

    <img src ="https://github.com/user-attachments/assets/17b69590-aec3-4551-bd04-95b2414560d3" height="300px">

  * **FOR 3.12 ONLY**:
    The `zlib1.dll` should be placed in the `DLLs` folder

    <img src ="https://github.com/user-attachments/assets/a48f9695-5350-4971-8cbc-1a4119785ea3" height="100px">
   

    
    **Ensure**:
    
    *   `tcl` folder is at the root of the embedded distribution.
    *   `tkinter` folder is also at the root of the embedded distribution.
    *   `_tkinter.pyd`, `tcl86t.dll`, `tk86t.dll`, and `zlib1.dll` are in the `DLLs` folder.
    *    **IMPORTANT:** Either replace `python312._pth` with the one provided or edit your current `python312._pth` to include `./DLLs`.
5.  **Test Tkinter**: Run this command to confirm Tkinter is properly installed:
    
    `python -m tkinter`

<img src ="https://github.com/user-attachments/assets/2ce5bdc2-c2e0-4ff8-aa18-ced238376347" height="300px">

---

### 🎉 **All Done!** 🎉

You’re now ready to use Tkinter with your embedded Python distribution. If you encounter any issues, double-check the folder structure and file placements, and ensure you’ve followed the instructions for your specific Python version. Happy coding! 🚀
