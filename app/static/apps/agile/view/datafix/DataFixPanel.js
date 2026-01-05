Ext.define("AgileAcpt.view.datafix.DataFixPanel", {
  extend: "Ext.form.Panel",
  xtype: "datafix-panel",
  title: "Data Fix Scripts",
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
      xtype: "textfield",
      fieldLabel: "Agile Username",
      name: "agileUser",
      allowBlank: false,
      emptyText: "Enter Agile PLM username",
    },
    {
      xtype: "textfield",
      fieldLabel: "Agile Password",
      name: "agilePassword",
      inputType: "password",
      allowBlank: false,
      emptyText: "Enter Agile PLM password",
      triggers: {
        eye: {
          cls: "fas fa-eye",
          handler: function (field) {
            var trigger = field.getTrigger("eye");
            if (field.inputType === "password") {
              field.inputType = "text";
              field.inputEl.dom.type = "text";
              trigger.el.replaceCls("fa-eye", "fa-eye-slash");
            } else {
              field.inputType = "password";
              field.inputEl.dom.type = "password";
              trigger.el.replaceCls("fa-eye-slash", "fa-eye");
            }
          },
        },
      },
    },
    {
      xtype: "filefield",
      fieldLabel: "Fix Script File",
      name: "fixScriptFile",
      allowBlank: false,
      buttonText: "Browse...",
      emptyText: "Select data fix script file",
      accept: ".sql,.txt",
      regex: /\.(sql|txt)$/i,
      regexText: "Only SQL or TXT files are allowed",
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
          Ext.Msg.alert("Info", "Executing DataFix job for environment: " + values.targetEnv);
          // TODO: Implement actual API call to trigger DataFix job
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
