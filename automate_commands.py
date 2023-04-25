from subprocess import (
    run,
    Popen,
    PIPE,
    STDOUT,
    TimeoutExpired
)
import os
import time
import sys
import signal
from datetime import datetime

class Linux(object):
    def __init__(self):
        self.current_dir = None

    def execute_command(self, command, timeout = 5):
        """
        
        """
        command = self._process_command(command)

        # try:
        #     print("Enter try block")
        #     process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, start_new_session=True)
        #     process.wait(timeout=timeout)
        #     print("After wait")

        # except TimeoutExpired:
        #     print("In except")
        #     # stdout = process.stdout.readlines()
        #     print(process.stdout.flush())
        #     os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        #     # for lines in stdout:
        #     #     print(lines.decode()[:-1])
        
        with open("/home/phani/react/automation/log.txt", 'wb') as out:
            process = Popen(command, stdout=out, stdin=PIPE, stderr=out)
        # stdout, stderr = process.communicate()
        # stdout = stdout.decode()
        # stderr = stderr.decode()
        
        time.sleep(timeout)
        
        # stdout = process.stdout.readlines()
        process.terminate()
        # for lines in stdout:
        #     print(lines.decode()[:-1])
        

        
        # print(stdout)
        # if stderr != "":
        #     print(stderr)
        #     return False


        # stdout, stderr = run(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, timeout = timeout)
        
        # stdout = stdout.decode()
        # stderr = stderr.decode()
        
        # # For DEBUG purposes - Uncomment when needed  
        # # print(stdout)

        # if stderr != "":
        #     print(stderr)
        #     return False

        return True


    def interact_with_script_once(self, command, input):
        """
        
        """    
        command = self._process_command(command)
        process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(str.encode(input))        
        stdout = stdout.decode()
        stderr = stderr.decode()
        
        if stderr != "":
            print(stderr)
            return False

        return True

    def interact_with_script(self, command, input_list, response_list, ENABLE_LOGGING = False, filename = None):
        """
        response_list follows the following structure:
        [response1, response2, ..., responseN, terminating_condition]
        """
        command = self._process_command(command)
        process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_log = ""
        stderr_log = ""
        
        for (input, response) in zip(input_list[:-1], response_list[:-1]):
            # Prepare the input to the script and expected response
            # from the script
            input = input + "\n"
            response = response + "\n"

            stdout_log = stdout_log + self._search_for_output(response, process)
            
            # Write input
            process.stdin.write(str.encode(input))
            process.stdin.flush()
            
            # Capture output
            stdout = process.stdout.readline().decode()
            stdout_log = stdout_log + stdout

            # Check for errors occured (if any)
            if process.returncode != None:
                if process.returncode < 0:
                    return False
        
        # Prepare the final input to the script and expected 
        # response from the script
        input = input_list[-1] + "\n"
        response = response_list[-1] + "\n"

        # Write input
        stdout_log = stdout_log + self._search_for_output(response, process)
        
        # Capture the stdout and stderr
        stdout, stderr = process.communicate(str.encode(input))        
        stdout = stdout.decode()
        stderr = stderr.decode()
        stdout_log = stdout_log + stdout
        stderr_log = stderr_log + stderr

        # For DEBUG purposes - Uncomment when needed  
        # print(stdout_log)

        if ENABLE_LOGGING:
            self._logger(filename = filename, stdout_log = stdout_log, stderr_log = stderr_log)

        # Check for errors occured (if any)
        if stderr != "":
            print(stderr)
            return False

        return True
        
    def _process_command(self, command):
        return command.split()

    def _get_char(self, process):
        """
        automate.py
        """
        # Read the available next one byte
        character = process.stdout.read1(1)
        
        # For DEBUG purposes - Uncomment when needed
        print(
            character.decode("utf-8"),
            end="",
            flush=True,  # Unbuffered print
        )

        return character.decode("utf-8")

    def _search_for_output(self, string, process):
        """
        
        """
        buffer = ""
        while not string in buffer:
            buffer = buffer + self._get_char(process)

        return buffer

    def _logger(self, filename = None, stdout_log = "", stderr_log = ""):
        """
        
        """
        line_separator = self._line_separator("=")

        # If no filename has been given, then a default the filename would
        # be YYYY-MM-DD_hr_min_sec.txt
        if filename is None:
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")

        try:
            if stdout_log != "":
                with open(filename, "w") as text_file:
                    print(f"{stdout_log}", file=text_file)

                if stderr_log != "":
                    with open(filename, "a") as text_file:
                        print(f"{separator}", file=text_file)
                        print(f"{stderr_log}", file=text_file)

            elif stderr_log != "":
                with open(filename, "w") as text_file:
                    print(f"{stderr_log}", file=text_file)
            
            else:
                pass
        except:
            print("Unable to open the file")

        return

    def _line_separator(self, character, count = 10):
        """
        
        """
        line_separator = character * count + "\n"
        return line_separator

    def get_current_dir(self):
        """
        
        """
        command = ["pwd"]
        self.current_dir = run(command, text=True, stdout=PIPE, stderr=STDOUT, timeout=1).stdout
        return self.current_dir

    def list_directory_contents(self, all=False, longList=False):
        """
        
        """
        command = ["ls"]

        if all:
            command.append("-a")
        if longList:
            command.append("-l")
        
        return run(command, text=True, stdout=PIPE, stderr=STDOUT, timeout=1).stdout

    def change_directory(self, directory):
        """
        directory
        """
        cmd = "cd " + directory + " && pwd" # add the pwd command to run after, this will get our directory after running cd
        process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True) # run our new command
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        # Read the output
        if stdout != "":
            # For DEBUG purposes - Uncomment when needed
            # print(stdout)
            
            # If we did get a directory, go to there while ignoring the newline 
            os.chdir(stdout[0:len(stdout) - 1])
            
        if stderr != "":
            # For DEBUG purposes - Uncomment when needed
            print(stderr) # if that directory doesn't exist, bash/sh/whatever env will complain for us, so we can just use that
            return False

        return True    
