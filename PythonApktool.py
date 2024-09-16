import os
import subprocess
import platform
from colorama import Fore, Style
import glob


class ApkTool:
    def __init__(self, apktool_path=None, apksigner_path=None, zipalign_path=None, keystore_path=None, keystore_alias='androiddebugkey', keystore_password='android', include_paths_in_messages=False):
        self.apktool_path = self._adjust_path(apktool_path) if apktool_path else self._find_tool('apktool')
        if not self.apktool_path:
            raise FileNotFoundError("apktool not found in system PATH.")

        self.apksigner_path = self._adjust_path(apksigner_path) if apksigner_path else self._find_tool('apksigner')
        if not self.apksigner_path:
            raise FileNotFoundError("apksigner not found in system PATH.")

        self.zipalign_path = self._adjust_path(zipalign_path) if zipalign_path else self._find_tool('zipalign')
        if not self.zipalign_path:
            raise FileNotFoundError("zipalign not found in system PATH.")

        # Set the keystore path
        if keystore_path:
            self.keystore_path = self._adjust_path(keystore_path)
        else:
            # Default keystore path is SignKey/debug.keystore
            self.keystore_path = os.path.join(os.getcwd(), 'SignKey', 'debug.keystore')

        self.keystore_alias = keystore_alias
        self.keystore_password = keystore_password

        self.include_paths_in_messages = include_paths_in_messages

    def _find_tool(self, tool_name):
        """Finds the executable path of a tool using system commands."""
        os_name = platform.system()

        if os_name == 'Windows':
            cmd = ['where', tool_name]
        else:
            cmd = ['which', tool_name]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            tool_path = result.stdout.strip()
            if not tool_path:
                return None
            return tool_path
        except subprocess.CalledProcessError:
            return None

    def _adjust_path(self, path):
        """Adjusts relative paths to absolute paths based on the current working directory."""
        if path and not os.path.isabs(path):
            return os.path.join(os.getcwd(), path)
        return path

    def _print_log(self, process):
        """Reads and prints apktool logs with custom formatting."""
        try:
            for line in iter(process.stdout.readline, b''):
                decoded_line = line.decode('utf-8', errors='replace').strip()
                if decoded_line.startswith('I:'):
                    print(Fore.BLUE + decoded_line + Style.RESET_ALL)
                elif decoded_line.startswith('W:'):
                    print(Fore.YELLOW + decoded_line + Style.RESET_ALL)
                elif decoded_line.startswith('E:'):
                    print(Fore.RED + decoded_line + Style.RESET_ALL)
                else:
                    if "Press any key to continue" not in decoded_line:
                        print(decoded_line)
        except Exception as e:
            print(Fore.RED + f"Error while reading logs: {e}" + Style.RESET_ALL)

    def _run_cmd(self, cmd, show_log, success_message=None):
        """Runs a command and handles 'Press any key to continue' prompts by sending newline."""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE  # To send input if needed
            )
            # Send newline character to stdin to bypass any 'Press any key to continue' prompts
            process.stdin.write(b'\n')
            process.stdin.flush()

            if show_log:
                self._print_log(process)
            else:
                process.communicate()

            # Wait for the process to finish and get the return code
            return_code = process.wait()
            if return_code == 0:
                if success_message:
                    if self.include_paths_in_messages:
                        print(Fore.GREEN + success_message + Style.RESET_ALL)
                    else:
                        # Remove paths from the success message
                        message = success_message.split("'")[0]
                        print(Fore.GREEN + message.strip() + Style.RESET_ALL)
            else:
                error_message = f"Command failed with return code {return_code}"
                if not self.include_paths_in_messages:
                    error_message = error_message.split("'")[0]
                print(Fore.RED + error_message + Style.RESET_ALL)
        except Exception as e:
            error_message = f"Error during command execution: {e}"
            if not self.include_paths_in_messages:
                error_message = error_message.split("'")[0]
            print(Fore.RED + error_message + Style.RESET_ALL)

    def _sign_apk(self, apk_path):
        """Signs the APK with the provided keystore."""
        keystore_path = self.keystore_path

        if not os.path.exists(keystore_path):
            error_message = f"Keystore not found at {keystore_path}"
            if not self.include_paths_in_messages:
                error_message = "Keystore not found."
            print(Fore.RED + error_message + Style.RESET_ALL)
            return False

        # Build the apksigner command
        apksigner_cmd = [
            self.apksigner_path, 'sign',
            '--ks', keystore_path,
            '--ks-key-alias', self.keystore_alias,
            '--ks-pass', f'pass:{self.keystore_password}',
            '--key-pass', f'pass:{self.keystore_password}',
            '--v4-signing-enabled', 'false',
            apk_path
        ]

        try:
            subprocess.run(apksigner_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if self.include_paths_in_messages:
                print(Fore.GREEN + f"Successfully signed '{apk_path}' with keystore '{keystore_path}'." + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "Successfully signed." + Style.RESET_ALL)
            return True
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to sign APK: {e}"
            if not self.include_paths_in_messages:
                error_message = "Failed to sign APK."
            print(Fore.RED + error_message + Style.RESET_ALL)
            return False

    def _zipalign_apk(self, apk_path):
        """Aligns the APK using zipalign."""
        aligned_apk_path = apk_path.replace('.apk', '_aligned.apk')

        zipalign_cmd = [
            self.zipalign_path, '-v', '4',
            apk_path,
            aligned_apk_path
        ]

        try:
            subprocess.run(zipalign_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Replace the original APK with the aligned one
            os.remove(apk_path)
            os.rename(aligned_apk_path, apk_path)
            if self.include_paths_in_messages:
                print(Fore.GREEN + f"Successfully zipaligned '{apk_path}'." + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "Successfully zipaligned." + Style.RESET_ALL)
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to zipalign APK: {e}"
            if not self.include_paths_in_messages:
                error_message = "Failed to zipalign APK."
            print(Fore.RED + error_message + Style.RESET_ALL)

    def decompile(self, apk_path, output_dir=None, force=True, show_log=False):
        """
        Decompiles an APK file.

        :param apk_path: Path to the APK file.
        :param output_dir: Directory to place the decompiled files.
        :param force: Overwrite existing files without asking.
        :param show_log: Whether to display the apktool log.
        """
        apk_path = self._adjust_path(apk_path)
        output_dir = self._adjust_path(output_dir) if output_dir else None

        cmd = [self.apktool_path, 'd', apk_path]
        if force:
            cmd.append('-f')
        if output_dir:
            cmd.extend(['-o', output_dir])

        success_message = f"Successfully decompiled '{apk_path}'"
        self._run_cmd(cmd, show_log, success_message=success_message)

    def build(self, folder_path, output_apk=None, force=True, show_log=False):
        """
        Builds an APK from decompiled files, signs it with the provided keystore, and aligns it using zipalign.

        :param folder_path: Path to the decompiled folder.
        :param output_apk: Path to save the rebuilt APK.
        :param force: Overwrite existing files without asking.
        :param show_log: Whether to display the apktool log.
        """
        folder_path = self._adjust_path(folder_path)
        output_apk = self._adjust_path(output_apk) if output_apk else folder_path + "_Signed.apk"

        cmd = [self.apktool_path, 'b', folder_path]
        if force:
            cmd.append('-f')
        if output_apk:
            cmd.extend(['-o', output_apk])

        success_message = f"Successfully built '{folder_path}'"
        self._run_cmd(cmd, show_log, success_message=success_message)

        # Determine the path to the built APK
        if output_apk and os.path.exists(output_apk):
            apk_path = output_apk
        else:
            dist_dir = os.path.join(folder_path, 'dist')
            apk_files = glob.glob(os.path.join(dist_dir, '*.apk'))
            if apk_files:
                apk_path = apk_files[0]
            else:
                error_message = "No APK file found in dist directory after build."
                if not self.include_paths_in_messages:
                    error_message = "No APK file found after build."
                print(Fore.RED + error_message + Style.RESET_ALL)
                return

        # Sign the APK with the provided keystore
        signed = self._sign_apk(apk_path)
        if signed:
            # Align the APK using zipalign
            self._zipalign_apk(apk_path)

    def install_framework(self, apk_path, tag=None, force=True, show_log=False):
        """
        Installs framework resources.

        :param apk_path: Path to the framework APK.
        :param tag: Optional tag for the framework.
        :param force: Overwrite existing framework files.
        :param show_log: Whether to display the apktool log.
        """
        apk_path = self._adjust_path(apk_path)
        cmd = [self.apktool_path, 'if', apk_path]
        if force:
            cmd.append('-f')
        if tag:
            cmd.extend(['-t', tag])

        success_message = f"Successfully installed framework from '{apk_path}'"
        self._run_cmd(cmd, show_log, success_message=success_message)

    def empty_framework_dir(self, show_log=False):
        """
        Empties the apktool framework directory.

        :param show_log: Whether to display the apktool log.
        """
        cmd = [self.apktool_path, 'empty-framework-dir']

        success_message = "Successfully emptied the apktool framework directory"
        self._run_cmd(cmd, show_log, success_message=success_message)
