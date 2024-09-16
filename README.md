# Python-Apktool

![image](https://github.com/user-attachments/assets/2ee4710d-47eb-4541-acd8-8675cd811e15)



**Python-Apktool** is a Python library designed to streamline the decompiling, building, signing, and aligning of APK files. By utilizing `apktool`, `apksigner`, and `zipalign`, it offers a user-friendly interface for managing APK operations, simplifying complex tasks, and enabling efficient APK editing and rebuilding.

## Features

- **Decompile:** Easily decompile APK files into readable code.
- **Build:** Rebuild decompiled code into APK files, sign them with a keystore, and align the APK.
- **Sign APKs:** Sign APKs using a specified keystore and alias.
- **Zipalign APKs:** Optimize APK files using `zipalign`.
- **Install Framework:** Install framework resources required by APKtool.
- **Empty Framework Directory:** Clean the APKtool framework directory.

## Requirements

- Python 3.x
- Tools: `apktool`, `apksigner`, `zipalign` must be installed and available in the system PATH.

## Installation

To install Python-Apktool, clone the repository and install the required dependencies:

```bash
git clone https://github.com/QM4RS/Python-Apktool.git
cd Python-Apktool
pip install -r requirements.txt
```
## Usage
Here’s a basic example of how to use Python-Apktool:
```python
from PythonApktool import Apktool

# Initialize the apktool
apktool = Apktool(include_paths_in_messages=True)

# Decompile an APK file
apktool.decompile('path/to/your.apk')

# Build the decompiled files back into an APK
apktool.build('path/to/decompiled/folder')
```
## Decompiling an APK
To decompile an APK file:
```python
apktool.decompile('path/to/your.apk', output_dir='output/directory', force=True, show_log=True)
```
## Building an APK
To build an APK from decompiled files:
```python
apktool.build('path/to/decompiled/folder', output_apk='output.apk', force=True, show_log=True)
```
## Signing an APK
To sign an APK with a keystore:
```python
apktool._sign_apk('path/to/your.apk')
```
## Aligning an APK
To align an APK using zipalign:
```python
apktool._zipalign_apk('path/to/your.apk')
```
## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.
## License
This project is licensed under the MIT License - see the LICENSE file for details.
## Acknowledgments
Special thanks to the developers of apktool, apksigner, and zipalign for providing the essential tools this apktool is built upon.
