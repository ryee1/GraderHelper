import os
import subprocess
import traceback
import shutil
import time

class Tester:
    def __init__(self, assignment_folder_name, test_run=False, test_driver_file=None,
                 test_output_file="testoutput.txt", test_driver_dir="testdriver"):
        self.test_driver_dir = test_driver_dir
        self.assignment_folder_name = assignment_folder_name
        self.test_driver_file = test_driver_file
        self.test_output_file = test_output_file
        self.assignment_folder_path = os.path.join(os.getcwd(), assignment_folder_name)
        self.test_run = test_run

    def run_sys_prog_driver(self, test_file_path, output_path):
        print("RUN SYS PROG DRIVER")
        with open(test_file_path) as f:
            cmds = [line.rstrip("\n") for line in f if line.strip()]

        output = ""
        error = ""
        stdout = ""
        print("cmds", cmds)
        print("DIRNAME: ", os.path.dirname(test_file_path))
        original_dir = os.getcwd()
        os.chdir(os.path.dirname(test_file_path))
        for cmd in cmds:
            try:
                c = cmd.split(" ")
                print(c)
                p = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                stdout, error = p.communicate()
                output += (stdout + error)
                print(output)
            except:
                print("ERROR", error)
        os.chdir(original_dir)
        self.save_output(output, output_path)
        return output

    def compile_c_driver(self, root, test_executable_path):
        original_wd = os.getcwd()
        os.chdir(root)
        compiler = "gcc"
        cflag = ""
        compileflag = "-o"
        compile_path = "ss.c"
        executable_path = test_executable_path

        #os.system("g++ -std=c++11 *.cpp -o output")

        args = [compiler, cflag, compile_path, compileflag,
                "ss"]
        print("COMPILE_DRIVER", compile_path, executable_path)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = p.communicate()[1]

        os.chdir(original_wd)
        return output

    def compile_driver(self, root, test_executable_path):
        original_wd = os.getcwd()
        os.chdir(root)
        compiler = "g++"
        cflag = "-std=c++11"
        compileflag = "-o"
        compile_path = "ss.s"
        executable_path = test_executable_path
        #os.system("g++ -std=c++11 *.cpp -o output")

        args = [compiler, cflag, compile_path, compileflag,
                executable_path]
        print("COMPILE_DRIVER", compile_path, executable_path)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = p.communicate()[1]

        os.chdir(original_wd)
        return output

    def run_cpp_driver(self,root, test_executable_path):
        original_wd = os.getcwd()
        try:
            os.chdir(root)
            p = subprocess.Popen([test_executable_path], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE, universal_newlines=True)
            output = p.communicate()[0]
        finally:
            os.chdir(original_wd)
        return output

    def save_output(self, output, output_path):
        with open(output_path, 'w+') as out:
            out.write(output)

    def find_driver(self, root):
        folder = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
        print(root, len(folder))
        if len(folder) == 0:
            return None
        if self.test_driver_file is not None:
            test_driver_path = os.path.join(os.getcwd(), self.test_driver_dir, self.test_driver_file)
            new_driver_path = os.path.join(root, self.test_driver_file)
            shutil.copyfile(test_driver_path, new_driver_path)
            return new_driver_path
        else:
            return os.path.join(root, "output")

    def rename_files(self, root, files):
        if len(files) == 1:
            filename = files[0]
            os.rename(os.path.join(root, filename), os.path.join(root, "ss.c"))

    def loop_and_test_all_dirs(self):
        for root, folders, files in os.walk(self.assignment_folder_path):

            if self.test_driver_file is not None:
                self.rename_files(root, files)

            test_file_path = self.find_driver(root)
            if test_file_path is None:
                print("test_file_path is None", root, files)
                continue
            test_executable_path = os.path.join(root, "ss")
            print(test_file_path, test_executable_path, root, files)
            output = ""
            try:
                output = self.compile_c_driver(root, test_executable_path) + "\n"
                #output = self.compile_driver(root, test_executable_path) + "\n"
                output = self.run_sys_prog_driver(test_file_path,  os.path.join(root, self.test_output_file))
                #output = self.run_cpp_driver(root, test_executable_path)
                self.save_output(output, os.path.join(root, self.test_output_file))
            except Exception:
                output += traceback.format_exc()
                self.save_output(output, os.path.join(root, "Error" + self.test_output_file))
                os.rename(root, root + "_Error")
            # finally:
            #     if self.test_driver_file is not None:
            #         os.remove(test_file_path)

            if self.test_run:
                return


if __name__ == "__main__":
    tester = Tester("CS3560_", test_run=False, test_driver_file="test")
    tester.loop_and_test_all_dirs()
