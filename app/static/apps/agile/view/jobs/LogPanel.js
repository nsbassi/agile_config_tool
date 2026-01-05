Ext.define('AgileAcpt.view.jobs.LogPanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'log-panel',
    layout: 'fit',
    bodyPadding: 5,
    items: [{
        xtype: 'textarea',
        reference: 'logArea',
        readOnly: true,
        style: 'font-family: monospace;'
    }]
});
