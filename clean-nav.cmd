@echo off
setlocal
set "VBS=%TEMP%\clean-nav.vbs"

rem Write a tiny VBScript that cleans all .html files recursively
>"%VBS%" (
  echo Set fso = CreateObject("Scripting.FileSystemObject")
  echo Set re = New RegExp
  echo re.Global = True
  echo re.IgnoreCase = True
  echo
  echo Sub CleanFile(p)
  echo   On Error Resume Next
  echo   Set f = fso.OpenTextFile(p, 1, False)
  echo   s = f.ReadAll
  echo   f.Close
  echo   orig = s
  echo
  echo   ' 1) Remove the "Dynamic Nav: wire every page" block up to </script>
  echo   re.Pattern = "/\*[\-\s]*Dynamic Nav: wire every page[\s\S]*?</script>"
  echo   s = re.Replace(s, "</script>")
  echo
  echo   ' 2) Remove any <script> that defines function injectNav(...)
  echo   re.Pattern = "<script[^>]*>[\s\S]*?function\s+injectNav\s*\([\s\S]*?</script>"
  echo   s = re.Replace(s, "")
  echo
  echo   ' 3) Remove inline template chunks like: dropdown = `...`;
  echo   re.Pattern = "dropdown\s*=\s*`[\s\S]*?`;"
  echo   s = re.Replace(s, "")
  echo
  echo   ' 4) Remove container.innerHTML = `...`;
  echo   re.Pattern = "container\.innerHTML\s*=\s*`[\s\S]*?`;"
  echo   s = re.Replace(s, "")
  echo
  echo   ' 5) Remove any leftover comment line mentioning Dynamic Nav
  echo   re.Pattern = "/\*[\s\S]*?Dynamic Nav: wire every page[\s\S]*?\*/"
  echo   s = re.Replace(s, "")
  echo
  echo   If s ^<> orig Then
  echo     Set w = fso.OpenTextFile(p, 2, False)
  echo     w.Write s
  echo     w.Close
  echo     WScript.Echo "Cleaned: " ^& p
  echo   End If
  echo End Sub
  echo
  echo Sub Walk(d)
  echo   For Each f In d.Files
  echo     If LCase(fso.GetExtensionName(f.Path)) = "html" Then CleanFile f.Path
  echo   Next
  echo   For Each sd In d.SubFolders
  echo     Walk sd
  echo   Next
  echo End Sub
  echo
  echo Walk fso.GetFolder(".")
)

rem Run the cleaner
cscript //nologo "%VBS%"
echo Done.
