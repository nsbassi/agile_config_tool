Ext.define("AgileAcpt.controller.Job", {
  extend: "Ext.app.ViewController",
  alias: "controller.job",

  onRefreshJobs: function () {
    var grid = this.lookupReference("jobGrid");
    if (grid) {
      grid.getStore().load();
    }
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

  onViewLogAction: function (grid, rowIndex, colIndex) {
    var record = grid.getStore().getAt(rowIndex);
    var jobId = record.get("id");
    var jobType = record.get("type");

    // For ACP export/import/file-copy jobs, try to get the ACP log file first
    if (jobType === "acp-export" || jobType === "acp-import" || jobType === "file-copy") {
      Ext.Ajax.request({
        url: "/api/jobs/" + jobId + "/acp-log",
        method: "GET",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("jwt"),
        },
        success: function (response) {
          var data = Ext.decode(response.responseText);
          this.showLogWindow(jobId, jobType, data.log, data.filename);
        },
        failure: function (response) {
          // If ACP log not found, fall back to job log
          this.fetchAndShowJobLog(jobId, jobType);
        },
        scope: this,
      });
    } else {
      // For other job types, show the regular job log
      this.fetchAndShowJobLog(jobId, jobType);
    }
  },

  fetchAndShowJobLog: function (jobId, jobType) {
    Ext.Ajax.request({
      url: "/api/jobs/" + jobId + "/log?offset=0",
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("jwt"),
      },
      success: function (response) {
        var data = Ext.decode(response.responseText);
        this.showLogWindow(jobId, jobType, data.chunk, "job.log");
      },
      failure: function (response) {
        Ext.Msg.alert("Error", "Failed to load job log");
      },
      scope: this,
    });
  },

  showLogWindow: function (jobId, jobType, logContent, filename) {
    var win = Ext.create("Ext.window.Window", {
      title: "Job Log: " + jobId + " (" + jobType + ") - " + filename,
      width: 900,
      height: 600,
      layout: "fit",
      modal: false,
      maximizable: true,
      items: [
        {
          xtype: "textarea",
          readOnly: true,
          value: logContent,
          style: {
            fontFamily: "monospace",
            fontSize: "12px",
          },
        },
      ],
      buttons: [
        {
          text: "Download",
          iconCls: "fas fa-download",
          handler: function () {
            // Create a blob and download it
            var blob = new Blob([logContent], { type: "text/plain" });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = filename || jobId + ".log";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          },
        },
        {
          text: "Close",
          handler: function () {
            win.close();
          },
        },
      ],
    });
    win.show();
  },

  onDeleteJobAction: function (grid, rowIndex, colIndex) {
    var record = grid.getStore().getAt(rowIndex);
    var jobId = record.get("id");
    var jobType = record.get("type");

    Ext.Msg.confirm(
      "Delete Job",
      'Are you sure you want to delete job "' + jobId + '" (' + jobType + ")?",
      function (btn) {
        if (btn === "yes") {
          Ext.Ajax.request({
            url: "/api/jobs/" + jobId,
            method: "DELETE",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("jwt"),
            },
            success: function () {
              grid.getStore().remove(record);
              Ext.toast({
                html: "Job deleted successfully",
                closable: false,
                align: "tr",
                slideInDuration: 400,
              });
            },
            failure: function (response) {
              var error = Ext.decode(response.responseText, true);
              Ext.Msg.alert("Error", error?.error || "Failed to delete job");
            },
          });
        }
      }
    );
  },
});
