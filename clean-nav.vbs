' clean-nav.vbs — remove stray inline nav code from all .html files (recursive)
Option Explicit
Dim fso : Set fso = CreateObject("Scripting.FileSystemObject")

Sub CleanFile(p)
  On Error Resume Next
  Dim ts, s, orig
  Set ts = fso.OpenTextFile(p, 1, False)  ' ForReading
  s = ts.ReadAll : ts.Close
  orig = s

  Dim re : Set re = New RegExp
  re.Global = True : re.IgnoreCase = True

  ' 1) Kill the /* Dynamic Nav: wire every page */ ... </script> block
  re.Pattern = "/\*[\-\s]*Dynamic Nav: wire every page[\s\S]*?</script>"
  s = re.Replace(s, "</script>")

  ' 2) Remove any <script> that defines function injectNav(...)
  re.Pattern = "<script[^>]*>[\s\S]*?function\s+injectNav\s*\([\s\S]*?</script>"
  s = re.Replace(s, "")

  ' 3) Remove multiline template: dropdown = ` ... `;
  re.Pattern = "dropdown\s*=\s*`[\s\S]*?`;"
  s = re.Replace(s, "")

  ' 4) Remove multiline template: container.innerHTML = ` ... `;
  re.Pattern = "container\.innerHTML\s*=\s*`[\s\S]*?`;"
  s = re.Replace(s, "")

  ' 5) Remove any leftover comment mentioning Dynamic Nav
  re.Pattern = "/\*[\s\S]*?Dynamic Nav: wire every page[\s\S]*?\*/"
  s = re.Replace(s, "")

  If s <> orig Then
    Set ts = fso.OpenTextFile(p, 2, False) ' ForWriting
    ts.Write s : ts.Close
    WScript.Echo "Cleaned: " & p
  End If
End Sub

Sub Walk(d)
  Dim f, sf
  For Each f In d.Files
    If LCase(fso.GetExtensionName(f.Path)) = "html" Then CleanFile f.Path
  Next
  For Each sf In d.SubFolders
    Walk sf
  Next
End Sub

Walk fso.GetFolder(".")
