import os
import subprocess


class FileUtils:

    @staticmethod
    def run_external_reader(folder: str, filename: str, split_lines: bool=True):
        file_path = os.path.join(folder, filename)
        reader_exec = os.path.join(os.path.dirname(__file__), "FileReader", "bin", "Release", "net9.0", "win-x64", "publish", "FileReader.exe")

        print(f"Running {file_path} reader")
        try:
            result = subprocess.run(
                [reader_exec, file_path],
                capture_output=True,
                text=True,
                encoding="latin-1")
            if result.returncode == 0:
                output = result.stdout
                if split_lines:
                    return output.splitlines()
                else:
                    return output
            else:
                print(f"Error in reader execution: {result.stderr}")

        except FileNotFoundError as e:
            print(f"Error calling C# reader {e}")
