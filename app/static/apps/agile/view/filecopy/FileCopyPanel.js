Ext.define("AgileAcpt.view.filecopy.FileCopyPanel", {
  extend: "Ext.form.Panel",
  xtype: "filecopy-panel",
  title: "File Copy Operations",
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
      fieldLabel: "Target Environment",
      name: "targetEnv",
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
          "destJdbcUrl",
          "destTnsName",
          "destOracleHome",
          "destDbUser",
          "destDbPassword",
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
      xtype: "filefield",
      fieldLabel: "FileCopy Config File",
      name: "configFile",
      allowBlank: false,
      buttonText: "Browse...",
      emptyText: "Select FileCopy configuration file",
      accept: ".xml",
      regex: /\.xml$/i,
      regexText: "Only XML files are allowed",
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
          Ext.Msg.alert("Info", "Executing FileCopy job for environment: " + values.targetEnv);
          // TODO: Implement actual API call to trigger FileCopy job
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
