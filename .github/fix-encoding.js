// fix-encoding.js  (run with:  cscript //nologo fix-encoding.js .)
var fso = new ActiveXObject("Scripting.FileSystemObject");
var ForReading = 1, ForWriting = 2;
var adTypeText = 2, adSaveCreateOverWrite = 2;

var replacements = {
  "â€¦":"…", "Â©":"©", "Â®":"®",
  "â€“":"–", "â€”":"—",
  "â€˜":"‘", "â€™":"’",
  "â€œ":"“", "â€":"”",
  "Â·":"·",  "â€¢":"•",
  "Â ":" "   // stray NBSP shown as 'Â '
};

function readText(path, charset){
  var s = new ActiveXObject("ADODB.Stream");
  s.Type = adTypeText; s.Charset = charset; s.Open(); s.LoadFromFile(path);
  var t = s.ReadText(); s.Close(); return t;
}
function writeUtf8(path, text){
  var s = new ActiveXObject("ADODB.Stream");
  s.Type = adTypeText; s.Charset = "utf-8"; s.Open(); s.WriteText(text);
  s.SaveToFile(path, adSaveCreateOverWrite); s.Close();
}
function fixHtmlMeta(text){
  var re = /<meta\s+charset=["']?utf-8["']?/i;
  if (!re.test(text)){
    // insert right after <head>
    return text.replace(/(<head[^>]*>)/i, "$1\r\n    <meta charset=\"UTF-8\">");
  }
  return text;
}
function fixMojibake(text){
  for (var k in replacements){ text = text.split(k).join(replacements[k]); }
  return text;
}
function processFile(path){
  var ext = path.slice(path.lastIndexOf(".")).toLowerCase();
  var text;
  try { text = readText(path, "utf-8"); }
  catch(e){ text = readText(path, "windows-1252"); } // fallback

  var orig = text;
  if (ext === ".html") text = fixHtmlMeta(text);
  text = fixMojibake(text);

  if (text !== orig){
    writeUtf8(path, text);
    WScript.Echo("fixed: " + path);
  }
}
function walk(dir){
  var folder = fso.GetFolder(dir), e, sub;
  var fc = new Enumerator(folder.Files);
  for (; !fc.atEnd(); fc.moveNext()){
    e = fc.item().Path;
    var low = e.toLowerCase();
    if (low.endsWith(".html") || low.endsWith(".js")) processFile(e);
  }
  var sc = new Enumerator(folder.SubFolders);
  for (; !sc.atEnd(); sc.moveNext()){
    sub = sc.item().Path;
    walk(sub);
  }
}

// entry
var start = WScript.Arguments.length ? WScript.Arguments(0) : ".";
walk(fso.GetAbsolutePathName(start));
WScript.Echo("done.");
