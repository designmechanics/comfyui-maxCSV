import { app } from "/scripts/app.js";

app.registerExtension({
  name: "Max.CSVLoader",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name === "Max_CSV_Loader_Dynamic") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

        const widget = this.widgets.find((w) => w.name === "selected_row");
        const originalCallback = widget.callback;
        widget.callback = (value, ...args) => {
          if (originalCallback) {
            originalCallback.call(this, value, ...args);
          }
          const csv_file = this.widgets.find((w) => w.name === "csv_file").value;
          const selected_row = value;
          const url = `/max_csv_browser/get_rows?csv_file=${csv_file}&selected_row=${selected_row}`;

          const iframe = document.createElement("iframe");
          iframe.src = url;
          iframe.style.width = "100%";
          iframe.style.height = "400px";
          this.addDOMWidget("csv_preview", "iframe", iframe);
        };
        return r;
      };
    }
  },
});
