Ext.define("AgileAcpt.controller.Main", {
  extend: "Ext.app.ViewController",
  alias: "controller.main",

  onLogout: function () {
    localStorage.removeItem("jwt");
    Ext.Ajax.setDefaultHeaders({});
    window.location.href = "/login";
  },

  onRefreshJobs: function (btn) {
    var grid = btn.up("grid");
    grid.getStore().load();
  },

  onNavigateToACP: function () {
    this.navigateToPanel("acpPanel");
  },

  onNavigateToAverify: function () {
    this.navigateToPanel("averifyPanel");
  },

  onNavigateToJobs: function () {
    this.navigateToPanel("jobsPanel");
  },

  onNavigateToConfig: function () {
    this.navigateToPanel("configPanel");
  },

  onNavigateToFileCopy: function () {
    this.navigateToPanel("filecopyPanel");
  },

  onNavigateToDataFix: function () {
    this.navigateToPanel("datafixPanel");
  },

  navigateToPanel: function (panelId) {
    var container = this.lookupReference("mainContainer");
    var panel = container.down("#" + panelId);
    if (panel) {
      container.getLayout().setActiveItem(panel);
    }
  },
});
