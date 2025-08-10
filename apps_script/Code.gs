function onOpen() {
  SpreadsheetApp.getUi().createMenu("Fast Search")
    .addItem("Open Search", "showSidebar")
    .addToUi();
}

function showSidebar() {
  var html = HtmlService.createTemplateFromFile("index").evaluate().setTitle("Fast Search");
  SpreadsheetApp.getUi().showSidebar(html);
}

function fetchRows_(sheetName, limit) {
  var sh = SpreadsheetApp.getActive().getSheetByName(sheetName) || SpreadsheetApp.getActiveSheet();
  var values = sh.getDataRange().getValues();
  return values.slice(0, limit || 2000);
}

function getData(payload) {
  var cfg = JSON.parse(payload);
  var rows = fetchRows_(cfg.sheet || null, cfg.limit || 20000);
  return JSON.stringify({ rows: rows });
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}
