Ext.define("AgileAcpt.view.acp.ACPPanel", {
  extend: "Ext.form.Panel",
  xtype: "acp-panel",
  title: "ACP Operations",
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
      fieldLabel: "Operation",
      name: "operation",
      allowBlank: false,
      editable: false,
      displayField: "name",
      valueField: "value",
      value: "export",
      store: {
        fields: ["name", "value"],
        data: [
          { name: "Export", value: "export" },
          { name: "Import", value: "import" },
          { name: "Deep Compare", value: "deepcompare" },
        ],
      },
      listeners: {
        change: function (combo, newValue) {
          var form = combo.up("form");
          var targetEnvField = form.down("[name=targetEnv]");
          var configFileField = form.down("[name=configFile]");

          if (newValue === "export") {
            targetEnvField.setVisible(false);
            targetEnvField.setDisabled(true);
            configFileField.setVisible(true);
            configFileField.setDisabled(false);
          } else {
            targetEnvField.setVisible(true);
            targetEnvField.setDisabled(false);
            configFileField.setVisible(false);
            configFileField.setDisabled(true);
          }
        },
      },
    },
    {
      xtype: "combo",
      fieldLabel: "Source Environment",
      name: "sourceEnv",
      allowBlank: false,
      editable: false,
      displayField: "tag",
      valueField: "tag",
      queryMode: "local",
      store: {
        fields: ["id", "tag", "agilePlmUrl", "propagationUser", "propagationPassword", "dbJdbcUrl"],
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
      fieldLabel: "Target Environment",
      name: "targetEnv",
      allowBlank: false,
      hidden: true,
      disabled: true,
      editable: false,
      displayField: "tag",
      valueField: "tag",
      queryMode: "local",
      store: {
        fields: ["id", "tag", "agilePlmUrl", "propagationUser", "propagationPassword", "dbJdbcUrl"],
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
      fieldLabel: "ACP Config File",
      name: "configFile",
      allowBlank: false,
      buttonText: "Browse...",
      emptyText: "Select ACP configuration file",
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
          var configFile = form.findField("configFile").fileInputEl.dom.files[0];

          if (!configFile) {
            Ext.Msg.alert("Error", "Please select a configuration file");
            return;
          }

          // Get environment details from store
          var sourceEnvField = form.findField("sourceEnv");
          var sourceEnvStore = sourceEnvField.getStore();
          var sourceEnvRecord = sourceEnvStore.findRecord("tag", values.sourceEnv);

          if (!sourceEnvRecord) {
            Ext.Msg.alert("Error", "Source environment not found");
            return;
          }

          var host = sourceEnvRecord.get("agilePlmUrl");
          var productLine = values.sourceEnv; // Use source env tag as product line

          // For import/deepcompare, we also need target environment
          if (values.operation === "import" || values.operation === "deepcompare") {
            var targetEnvField = form.findField("targetEnv");
            var targetEnvStore = targetEnvField.getStore();
            var targetEnvRecord = targetEnvStore.findRecord("tag", values.targetEnv);

            if (!targetEnvRecord) {
              Ext.Msg.alert("Error", "Target environment not found");
              return;
            }
          }

          Ext.Msg.wait("Uploading configuration file...", "Please wait");

          // First, upload the configuration file
          var formData = new FormData();
          formData.append("file", configFile);

          fetch("/api/jobs/upload", {
            method: "POST",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("jwt"),
            },
            body: formData,
          })
            .then(function (response) {
              if (!response.ok) {
                throw new Error("Failed to upload file");
              }
              return response.json();
            })
            .then(function (uploadData) {
              // Now create the job with the uploaded file path
              var endpoint = "";
              var requestData = {
                xmlConfig: uploadData.path,
                host: host,
                mode: "local",
                sourceEnv: values.sourceEnv,
              };

              if (values.operation === "export") {
                endpoint = "/api/jobs/acp/export";
                requestData.productLine = productLine;
              } else if (values.operation === "import") {
                endpoint = "/api/jobs/acp/import";
                // For import, we need the export bundle
                // This is a limitation - need to implement bundle upload/selection
                Ext.Msg.close();
                Ext.Msg.alert(
                  "Not Implemented",
                  "Import operation requires an export bundle to be specified. This feature needs to be enhanced to allow bundle selection."
                );
                return;
              } else if (values.operation === "deepcompare") {
                // Deep compare is not yet implemented on the backend
                Ext.Msg.close();
                Ext.Msg.alert(
                  "Not Implemented",
                  "Deep compare operation is not yet implemented in the backend."
                );
                return;
              }

              Ext.Msg.wait("Creating " + values.operation + " job...", "Please wait");

              return Ext.Ajax.request({
                url: endpoint,
                method: "POST",
                headers: {
                  Authorization: "Bearer " + localStorage.getItem("jwt"),
                  "Content-Type": "application/json",
                },
                jsonData: requestData,
              });
            })
            .then(function (response) {
              Ext.Msg.close();
              var data = Ext.decode(response.responseText);
              Ext.Msg.alert(
                "Success",
                values.operation.charAt(0).toUpperCase() +
                  values.operation.slice(1) +
                  " job created successfully. Job ID: " +
                  data.jobId,
                function () {
                  // Switch to jobs panel to view the job
                  var viewport = Ext.ComponentQuery.query("mainview")[0];
                  if (viewport) {
                    var controller = viewport.getController();
                    if (controller) {
                      controller.navigateToPanel("jobsPanel");
                    }
                  }
                }
              );
              form.reset();
            })
            .catch(function (error) {
              Ext.Msg.close();
              Ext.Msg.alert("Error", error.message || "Failed to create job");
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
