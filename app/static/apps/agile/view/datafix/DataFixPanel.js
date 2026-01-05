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
      accept: ".sh",
      regex: /\.sh$/i,
      regexText: "Only SH (shell script) files are allowed",
    },
    {
      xtype: "filefield",
      fieldLabel: "Input File (Excel)",
      name: "inputFile",
      allowBlank: false,
      buttonText: "Select File...",
      listeners: {
        change: function (filefield, value, oldvalue) {
          // Store the file object for later use
          var file = filefield.fileInputEl.dom.files[0];
          filefield.up("form").file = file;
        },
      },
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

          // Get the input file field and extract the actual filename
          var inputFileField = form.findField("inputFile");
          var inputFile = null;

          if (
            inputFileField &&
            inputFileField.fileInputEl &&
            inputFileField.fileInputEl.dom.files.length > 0
          ) {
            inputFile = inputFileField.fileInputEl.dom.files[0].name;
          }

          // If still no inputFile, show error
          if (!inputFile) {
            Ext.Msg.alert("Error", "Please select an input file");
            return;
          }

          Ext.Ajax.request({
            url: "/api/jobs/datafix/run",
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + localStorage.getItem("jwt"),
            },
            jsonData: {
              targetEnv: values.targetEnv,
              inputFile: inputFile,
              mode: "local",
            },
            success: function (response) {
              var data = Ext.decode(response.responseText);
              Ext.Msg.alert("Success", "Data Fix job started with ID: " + data.jobId, function () {
                // Switch to Jobs panel after user clicks OK
                var mainView = Ext.ComponentQuery.query("mainview")[0];
                if (mainView && mainView.getViewModel()) {
                  mainView.getViewModel().set("currentView", "jobs-panel");
                }
              });
            },
            failure: function (response) {
              var errorMsg = "Failed to start Data Fix job";
              if (response.responseText) {
                try {
                  var data = Ext.decode(response.responseText);
                  errorMsg = data.message || errorMsg;
                } catch (e) {}
              }
              Ext.Msg.alert("Error", errorMsg);
            },
          });
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
