Ext.define("AgileAcpt.controller.Config", {
  extend: "Ext.app.ViewController",
  alias: "controller.config",

  onAddEnvironment: function () {
    var form = this.lookup("envForm");
    form.reset();
    form.setHidden(false);
  },

  onEditEnvironment: function (grid, rowIndex, colIndex) {
    var record = grid.getStore().getAt(rowIndex);
    var form = this.lookup("envForm");
    form.loadRecord(record);
    form.setHidden(false);
  },

  onDeleteEnvironment: function (grid, rowIndex, colIndex) {
    var store = grid.getStore();
    var record = store.getAt(rowIndex);

    Ext.Msg.confirm(
      "Delete Environment",
      'Are you sure you want to delete "' + record.get("tag") + '"?',
      function (btn) {
        if (btn === "yes") {
          Ext.Ajax.request({
            url: "/api/environments/" + record.get("id"),
            method: "DELETE",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("jwt"),
            },
            success: function () {
              store.remove(record);
              Ext.toast({
                html: "Environment deleted successfully",
                closable: false,
                align: "tr",
                slideInDuration: 400,
              });
            },
            failure: function (response) {
              var error = Ext.decode(response.responseText, true);
              Ext.Msg.alert("Error", error?.error || "Failed to delete environment");
            },
          });
        }
      }
    );
  },

  onSaveEnvironment: function (btn) {
    var form = this.lookup("envForm").getForm();
    var grid = this.lookup("envGrid");
    var store = grid.getStore();

    if (form.isValid()) {
      var values = form.getValues();
      var record = form.getRecord();
      var isUpdate = record && !record.phantom;

      Ext.Ajax.request({
        url: isUpdate ? "/api/environments/" + values.id : "/api/environments",
        method: isUpdate ? "PUT" : "POST",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("jwt"),
          "Content-Type": "application/json",
        },
        jsonData: values,
        success: function (response) {
          var data = Ext.decode(response.responseText);
          if (isUpdate) {
            record.set(data);
          } else {
            store.add(data);
          }
          Ext.toast({
            html: "Environment saved successfully",
            closable: false,
            align: "tr",
            slideInDuration: 400,
          });
          form.reset();
          this.lookup("envForm").setHidden(true);
          store.load();
        },
        failure: function (response) {
          var error = Ext.decode(response.responseText, true);
          Ext.Msg.alert("Error", error?.error || "Failed to save environment");
        },
        scope: this,
      });
    }
  },

  onCancelEdit: function () {
    var form = this.lookup("envForm");
    form.reset();
    form.setHidden(true);
  },

  onExecutionModeChange: function (combo, newValue) {
    var remoteFieldset = this.lookup("remoteFieldset");
    if (newValue === "remote") {
      remoteFieldset.setVisible(true);
    } else {
      remoteFieldset.setVisible(false);
    }
  },

  onAuthTypeChange: function (radiogroup, newValue) {
    var passwordField = this.lookup("remotePassword");
    var sshKeyField = this.lookup("sshKeyPath");
    if (newValue.authType === "password") {
      passwordField.setVisible(true);
      sshKeyField.setVisible(false);
    } else {
      passwordField.setVisible(false);
      sshKeyField.setVisible(true);
    }
  },

  onSaveHostConfig: function () {
    var form = this.lookup("hostConfigForm").getForm();
    if (form.isValid()) {
      var values = form.getValues();
      localStorage.setItem("hostConfig", JSON.stringify(values));
      Ext.toast({
        html: "Host configuration saved successfully",
        closable: false,
        align: "tr",
        slideInDuration: 400,
      });
    }
  },

  init: function () {
    var savedConfig = localStorage.getItem("hostConfig");
    if (savedConfig) {
      try {
        var config = JSON.parse(savedConfig);
        var form = this.lookup("hostConfigForm");
        if (form) {
          form.getForm().setValues(config);
          if (config.executionMode === "remote") {
            this.lookup("remoteFieldset").setVisible(true);
          }
          if (config.authType === "sshkey") {
            this.lookup("remotePassword").setVisible(false);
            this.lookup("sshKeyPath").setVisible(true);
          }
        }
      } catch (e) {
        console.error("Failed to load host config:", e);
      }
    }
  },
});
