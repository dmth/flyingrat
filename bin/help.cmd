
@ECHO.
@ECHO -SETUP--------------------------------------------------
@CALL environment.cmd
@ECHO --------------------------------------------------------
@ECHO.
@ECHO -HELP---------------------------------------------------
@ECHO.
@ECHO You can install the server by running "install.cmd".
@ECHO To start the server, simply start the file "run.cmd".
@ECHO The file invokes the command:
@ECHO "python -m flyingrat.cli"
@ECHO The server provides some configurable parameters, especially the
@ECHO directory where the Mails are stored. Start the Server with the --help
@ECHO parameter, to see how it is used.
@ECHO This is the output of this command:
@ECHO.
@python -m flyingrat.cli --help
@ECHO.
@ECHO If you want to run the server in an arbitrary temp directory and on default ports, simply double click the file "run.cmd"
@ECHO In case you want to specify any parameters, you can pass the parameters described above to the run script, like;
@ECHO CALL run.cmd C:\users\intevation
@ECHO.
@PAUSE
