' remove-jobs-line.vbs — delete any line containing fetchAPI('/jobs') (and its const) from all .html files
Option Explicit
Dim fso : Set fso = CreateObject("Scripting.FileSystemObject")

Sub CleanFile(p)
  Dim ts, s, lines, i, ln, out, changed
  Set ts = fso.OpenTextFile(p, 1, False) ' ForReading
  s = ts.ReadAll : ts.Close

  lines = Split(s, vbCrLf)
  out = "" : changed = False

  For i = 0 To UBound(lines)
    ln = lines(i)
    If InStr(LCase(ln), "fetchapi('/jobs')") > 0 _
       Or (InStr(LCase(ln), "const jobs") > 0 And InStr(LCase(ln), "fetchapi(") > 0) Then
      changed = True ' skip this line
    Else
      out = out & ln
      If i < UBound(lines) Then out = out & vbCrLf
    End If
  Next

  ' Remove any now-empty <script>...</script>
  Dim re : Set re = New RegExp
  re.Global = True : re.IgnoreCase = True
  re.Pattern = "<script[^>]*>\s*</script>"
  out = re.Replace(out, "")

  If changed Then
    Set ts = fso.OpenTextFile(p, 2, False) ' ForWriting
    ts.Write out : ts.Close
    WScript.Echo "Cleaned: " & p
  End If
End Sub

Sub Walk(d)
  Dim f, sd
  For Each f In d.Files
    If LCase(fso.GetExtensionName(f.Path)) = "html" Then CleanFile f.Path
  Next
  For Each sd In d.SubFolders
    Walk sd
  Next
End Sub

Walk fso.GetFolder(".")
