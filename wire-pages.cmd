@echo off
:: Inject <script defer src="/assets/js/pages.js?v=1"></script> before </body> in all .html files (recursively)
:: Pure CMD + Windows Script Host (JScript). No PowerShell required.

cscript //nologo //E:JScript "%~f0" .
if errorlevel 1 exit /b 1
echo.
echo ✅ Injected pages.js into HTML files where needed.
goto :eof

/*** JScript ***/
var fso = new ActiveXObject("Scripting.FileSystemObject");
var shell = new ActiveXObject("WScript.Shell");
var args = WScript.Arguments;
var root = args.length ? args(0) : ".";

function injectInFolder(folderPath) {
  var folder = fso.GetFolder(folderPath);

  // Files in this folder
  for (var e = new Enumerator(folder.Files); !e.atEnd(); e.moveNext()) {
    var file = e.item();
    if (!/\.html?$/i.test(file.Name)) continue;

    var ts = fso.OpenTextFile(file.Path, 1, true);
    var s = ts.ReadAll();
    ts.Close();

    if (s.indexOf('/assets/js/pages.js') !== -1) continue; // already wired

    var low = s.toLowerCase();
    var idx = low.lastIndexOf("</body>");
    if (idx < 0) continue; // no </body>, skip

    var inject = '  <script defer src="/assets/js/pages.js?v=1"></script>\r\n';
    var out = s.substring(0, idx) + inject + s.substring(idx);

    var tsw = fso.OpenTextFile(file.Path, 2, true);
    tsw.Write(out);
    tsw.Close();

    WScript.Echo("Wired: " + file.Path);
  }

  // Recurse into subfolders
  for (var d = new Enumerator(folder.SubFolders); !d.atEnd(); d.moveNext()) {
    injectInFolder(d.item().Path);
  }
}

injectInFolder(root);
WScript.Quit(0);
