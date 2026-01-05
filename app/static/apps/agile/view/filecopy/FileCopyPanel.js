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
          var configFile = form.findField("configFile").getEl().down("input[type=file]").dom
            .files[0];

          // Show loading message
          Ext.Msg.wait("Starting File Copy job...", "Please wait");

          // Prepare request data
          var requestData = {
            targetEnv: values.targetEnv,
            mode: "local",
          };

          // Create job directly (in demo mode, config file is optional)
          Ext.Ajax.request({
            url: "/api/jobs/filecopy/run",
            method: "POST",
            headers: {
              Authorization: "Bearer" + localStorage.getItem("jwt"),
              "Content-Type": "application/json",
            },
            jsonData: requestData,
            success: function (response) {
              Ext.Msg.close();
              var data = Ext.decode(response.responseText);
              Ext.Msg.alert(
                "Success",
                "File Copy job created successfully! Job ID: " + data.jobId,
                function () {
                  // Navigate to jobs panel
                  var viewport = Ext.ComponentQuery.query("mainview")[0];
                  if (viewport) {
                    var controller = viewport.getController();
                    if (controller) {
                      controller.navigateToPanel("jobsPanel");

                      // Refresh jobs grid
                      var jobsGrid = controller.lookupReference("jobGrid");
                      if (jobsGrid) {
                        jobsGrid.getStore().reload();
                      }
                    }
                  }
                }
              );

              // Reset form
              form.reset();
            },
            failure: function (response) {
              Ext.Msg.close();
              var error = "Failed to create File Copy job";
              try {
                var data = Ext.decode(response.responseText);
                error = data.error || error;
              } catch (e) {}
              Ext.Msg.alert("Error", error);
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
