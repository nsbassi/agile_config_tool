Ext.define("AgileAcpt.view.jobs.JobsPanel", {
  extend: "Ext.panel.Panel",
  xtype: "jobs-panel",
  requires: ["AgileAcpt.view.jobs.JobGrid", "AgileAcpt.controller.Job"],
  controller: "job",
  layout: "border",
  items: [
    {
      region: "center",
      xtype: "grid",
      reference: "jobGrid",
      store: { type: "jobs" },
      selModel: "rowmodel",
      columns: [
        { text: "ID", dataIndex: "id", flex: 2 },
        { text: "Type", dataIndex: "type", flex: 1 },
        {
          text: "Status",
          dataIndex: "status",
          flex: 1,
          renderer: function (value) {
            var color =
              value === "success"
                ? "green"
                : value === "error"
                ? "red"
                : value === "running"
                ? "blue"
                : "gray";
            return (
              '<span style="color: ' +
              color +
              '; font-weight: bold;">' +
              value.toUpperCase() +
              "</span>"
            );
          },
        },
        {
          text: "Created",
          dataIndex: "createdAt",
          xtype: "datecolumn",
          format: "Y-m-d H:i:s",
          flex: 1,
        },
        {
          text: "Finished",
          dataIndex: "finishedAt",
          xtype: "datecolumn",
          format: "Y-m-d H:i:s",
          flex: 1,
        },
        { text: "Summary", dataIndex: "summary", flex: 2 },
        {
          xtype: "actioncolumn",
          text: "Actions",
          width: 110,
          items: [
            {
              iconCls: "fas fa-file-alt",
              tooltip: "View Log",
              handler: "onViewLogAction",
            },
            {
              iconCls: "fas fa-download",
              tooltip: "Download Output",
              handler: "onDownloadOutputAction",
              isDisabled: function (view, rowIndex, colIndex, item, record) {
                return record.get("status") !== "success";
              },
            },
            {
              iconCls: "fas fa-trash",
              tooltip: "Delete Job",
              handler: "onDeleteJobAction",
            },
          ],
        },
      ],
      tbar: [{ text: "Refresh", iconCls: "fas fa-sync", handler: "onRefreshJobs" }],
      listeners: {
        selectionchange: "onJobSelectionChange",
      },
    },
    {
      region: "south",
      xtype: "panel",
      reference: "logPanel",
      title: "Job Log",
      collapsible: true,
      collapsed: true,
      split: true,
      height: 300,
      layout: "fit",
      items: [
        {
          xtype: "textarea",
          reference: "logArea",
          readOnly: true,
          style: 'font-family: "Courier New", monospace; font-size: 12px;',
          bodyPadding: 5,
        },
      ],
      tbar: [
        {
          xtype: "component",
          reference: "logTitle",
          html: "<b>Select a job to view its log</b>",
        },
        "->",
        {
          text: "Clear",
          iconCls: "fas fa-times",
          handler: "onClearLog",
        },
      ],
    },
  ],
});
