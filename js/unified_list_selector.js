import { app } from "/scripts/app.js";

app.registerExtension({
    name: "Comfy.UnifiedListSelector.Creator",
    async nodeCreated(node) {
        if (node.constructor.type !== "UnifiedListSelector") {
            return;
        }

        const combo = node.addWidget(
            "combo",
            "selected_line",
            "(Entrez un chemin valide)",
            () => {
                node.graph.setDirtyCanvas(true);
            },
            { values: ["(Entrez un chemin valide)"] }
        );

        const listFileWidget = node.widgets.find((w) => w.name === "list_file");

        if (!listFileWidget) return;

        const updateOptions = async (filePath) => {
            let lines = [];
            let placeholder = "(Entrez un chemin valide)";

            if (filePath && filePath.trim()) {
                placeholder = "(Chargement...)";
                combo.value = placeholder;

                try {
                    const response = await fetch('/get_list_from_file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ file_path: filePath }),
                    });
                    if(response.ok) {
                        lines = await response.json();
                    }
                } catch (e) {
                    console.error("UnifiedListSelector: Erreur API", e);
                }
            }

            if (lines.length === 0) {
                placeholder = filePath ? "(Fichier vide ou non trouvé)" : "(Entrez un chemin valide)";
                lines.push(placeholder);
            }

            combo.options.values = lines;

            if (!lines.includes(combo.value)) {
                combo.value = lines[0];
            }

            node.graph.setDirtyCanvas(true);
        };

        const originalCallback = listFileWidget.callback;
        listFileWidget.callback = (value) => {
            if (originalCallback) {
                originalCallback.call(listFileWidget, value);
            }
            updateOptions(value);
        };

        setTimeout(() => updateOptions(listFileWidget.value), 100);
    },
});
