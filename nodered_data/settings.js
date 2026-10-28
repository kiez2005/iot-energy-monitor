module.exports = {
    flowFile: 'flows.json',
    credentialSecret: false,
    uiPort: process.env.PORT || 1880,
    diagnostics: {
        enabled: true,
        ui: true,
    },
    runtimeState: {
        enabled: false,
        ui: false,
    },
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    editorTheme: {
        projects: {
            enabled: false
        },
        page: {
            title: "Node-RED | Giám Sát Điện Năng Gia Đình"
        }
    }
};
