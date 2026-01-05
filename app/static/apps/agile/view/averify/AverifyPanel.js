Ext.define("AgileAcpt.view.averify.AverifyPanel", {
  extend: "Ext.form.Panel",
  xtype: "averify-panel",
  title: "Averify Operations",
  bodyPadding: 20,
  scrollable: true,
  layout: {
    type: "vbox",
    align: "center",
  },
  defaults: {
    width: 600,
    labelWidth: 150,
    margin: "10 0",
  },
  items: [
    {
      xtype: "combo",
      fieldLabel: "Environment",
      name: "environment",
      allowBlank: false,
      editable: false,
      displayField: "tag",
      valueField: "tag",
      queryMode: "local",
      store: {
        fields: [
          "id",
          "tag",
          "agilePlmUrl",
          "propagationUser",
          "propagationPassword",
          "dbJdbcUrl",
          "destJdbcUrl",
          "destTnsName",
          "destOracleHome",
        ],
        proxy: {
          type: "rest",
          url: "/api/environments",
          reader: {
            type: "json",
            rootProperty: "data",
          },
          headers: {
            Authorization: "Bearer " + localStorage.getItem("jwt"),
          },
        },
        autoLoad: true,
      },
    },
    {
      xtype: "combo",
      fieldLabel: "Run Option",
      name: "runOption",
      allowBlank: false,
      editable: false,
      value: "all",
      displayField: "name",
      valueField: "value",
      store: {
        fields: ["name", "value"],
        data: [
          { name: "All", value: "all" },
          { name: "Modules", value: "modules" },
          { name: "Reset Flags", value: "resetflags" },
          { name: "Tables", value: "tables" },
          { name: "Test Cases", value: "testcases" },
        ],
      },
      listeners: {
        change: function (combo, newValue) {
          var form = combo.up("form");
          var modulesField = form.down("[name=modules]");
          var tablesField = form.down("[name=tables]");
          var testcasesField = form.down("[name=testcases]");

          modulesField.setVisible(newValue === "modules");
          modulesField.setDisabled(newValue !== "modules");
          tablesField.setVisible(newValue === "tables");
          tablesField.setDisabled(newValue !== "tables");
          testcasesField.setVisible(newValue === "testcases");
          testcasesField.setDisabled(newValue !== "testcases");
        },
      },
    },
    {
      xtype: "textfield",
      fieldLabel: "Modules",
      name: "modules",
      hidden: true,
      disabled: true,
      emptyText: "e.g., ppm, pcpqm, checkNonAgileTables",
      helpText: "Comma-separated list of modules",
    },
    {
      xtype: "textfield",
      fieldLabel: "Tables",
      name: "tables",
      hidden: true,
      disabled: true,
      emptyText: "Comma-separated list of table names",
    },
    {
      xtype: "textfield",
      fieldLabel: "Test Cases",
      name: "testcases",
      hidden: true,
      disabled: true,
      emptyText: "e.g., AGIL-0000XXXXXX",
    },
    {
      xtype: "textfield",
      fieldLabel: "NLS Language",
      name: "nlsLang",
      value: "AMERICAN_AMERICA.AL32UTF8",
      allowBlank: false,
    },
    {
      xtype: "checkbox",
      fieldLabel: "Send Email",
      name: "sendEmail",
      inputValue: "true",
      uncheckedValue: "false",
      boxLabel: "Send Averify results via email",
    },
    {
      xtype: "textfield",
      fieldLabel: "Mail To Address",
      name: "toAddress",
      vtype: "email",
      emptyText: "recipient@example.com",
    },
    {
      xtype: "textfield",
      fieldLabel: "CC Address",
      name: "ccAddress",
      vtype: "email",
      emptyText: "cc@example.com",
    },
  ],
  buttons: [
    {
      text: "Execute",
      formBind: true,
      scale: "large",
      iconCls: "fa fa-play",
      handler: function (btn) {
        var form = btn.up("form").getForm();
        if (form.isValid()) {
          var values = form.getValues();
          Ext.Msg.alert(
            "Info",
            "Executing Averify (" + values.runOption + ") for environment: " + values.environment
          );
          // TODO: Implement actual API call to trigger Averify job
        }
      },
    },
    {
      text: "Reset",
      handler: function (btn) {
        btn.up("form").getForm().reset();
      },
    },
  ],
});
