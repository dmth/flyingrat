@ECHO.
@ECHO INSTALLING...
@ECHO.
@ECHO -SETUP--------------------------------------------------
@CALL environment.cmd
@ECHO --------------------------------------------------------
@ECHO.
@ECHO.
@ECHO Running Python setup
@ECHO --------------------------------------------------------
@ECHO.
@CD ..
@python setup.py install --user
@ECHO.
@ECHO --------------------------------------------------------
@ECHO.
@ECHO DONE
@ECHO.
@PAUSE
