import subprocess


def check_readability(lisp_file: str) -> int:
    lisp_code = f'''
    (handler-case
        (progn
          (with-open-file (s "{lisp_file}")
            (loop for form = (read s nil :eof)
                  until (eq form :eof)))
          (sb-ext:exit :code 0))
      (error (e)
        (format t "~A~%" e)
        (sb-ext:exit :code 1)))
    '''

    proc = subprocess.run(
        [
            "sbcl",
            "--non-interactive",
            "--eval", lisp_code
        ],
        capture_output=True,
        text=True
    )

    # Access potential errors: proc.stdout + proc.stderr
    success = proc.returncode
    if success > 0:
        success = 1
    return success
