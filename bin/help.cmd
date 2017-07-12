
@ECHO.
@ECHO -SETUP--------------------------------------------------
@CALL environment.cmd
@ECHO --------------------------------------------------------
@ECHO.
@ECHO -HELP---------------------------------------------------
@ECHO To run the server you need to use the install.cmd first.
@ECHO If you already installed the Server, you ca run it like described in:
@ECHO "python -m flyingrat.cli"
@ECHO This is the output of this command:
@ECHO.
@python -m flyingrat.cli --help
@ECHO.
@ECHO If you want to run the server in an arbitrary temp directory and on default ports, simply double click the file "run.cmd"
@ECHO In case you want to specify any parameters, you can pass the parameters described above to the run script, like;
@ECHO CALL run.cmd C:\users\intevation
@ECHO.
@PAUSE