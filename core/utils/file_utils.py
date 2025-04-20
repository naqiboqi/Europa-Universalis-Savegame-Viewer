"""
FileUtils module for reading text files using an external C# FileReader executable.

Handles encoding-specific file reading and returns the contents as a string or list of lines.
"""


import os
import subprocess


class FileUtils:

    @staticmethod
    def run_external_reader(folder: str, filename: str, file_encoding: str="latin-1", split_lines: bool=True):
        """Runs an external C# file reader executable to read the contents of a specified file.

        This function uses a compiled C# program (FileReader.exe) to read a text file
        using 'latin-1' encoding. The output can be returned as a list of lines or a single string.

        Args:
            folder (str): The directory where the target file is located.
            filename (str): The name of the file to read.
            file_encoding (str): The encoding to use when decoding the file output.
                Defaults to 'latin-1'.
            split_lines (bool): If True, returns a list of lines. If False, returns the a string.
                Defaults to True.

        Returns:
            list[str] | str: The contents of the file as a list of lines if `split_lines` is True,
                or as a single string if False.
                Returns an empty list or empty string if an error occurs.

        Raises:
            FileNotFoundError: If the target file or the reader executable is not found.
            RuntimeError: If the reader executable exits with a non-zero status code.
        """
        file_path = os.path.join(folder, filename)
        reader_exec = os.path.join(
            os.path.dirname(__file__), "FileReader", "bin", "Release", 
            "net9.0", "win-x64", "publish", "FileReader.exe")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Target file to read does not exist: {file_path}")
        if not os.path.isfile(reader_exec):
            raise FileNotFoundError(f"FileReader.exe not found at {reader_exec}")

        print(f"Running file reader. Reading: {file_path}")
        try:
            result = subprocess.run(
                [reader_exec, file_path],
                capture_output=True,
                text=True,
                encoding=file_encoding)
            if result.returncode != 0:
                raise RuntimeError(f"Reader exited with code {result.returncode}")

            return result.stdout.splitlines() if split_lines else result.stdout
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except RuntimeError as e:
            print(f"Error: {e}")

        return [] if split_lines else ""
