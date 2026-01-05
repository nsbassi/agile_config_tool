Ext.define("AgileAcpt.controller.Job", {
  extend: "Ext.app.ViewController",
  alias: "controller.job",

  onRefreshJobs: function () {
    var grid = this.getView();
    grid.getStore().load();
  },

  onViewJobLog: function () {
    var grid = this.getView();
    var selection = grid.getSelection()[0];
    if (!selection) {
      Ext.Msg.alert("Info", "Please select a job first");
      return;
    }
    // TODO: Open log panel with selected job
    Ext.Msg.alert("Info", "Job Log for: " + selection.get("id"));
  },

  onDownloadOutput: function () {
    var grid = this.getView();
    var selection = grid.getSelection()[0];
    if (!selection) {
      Ext.Msg.alert("Info", "Please select a job first");
      return;
    }
    var jobId = selection.get("id");
    var filename = prompt("Enter filename to download:");
    if (filename) {
      window.open("/api/jobs/" + jobId + "/download?filename=" + encodeURIComponent(filename));
    }
  },
});
