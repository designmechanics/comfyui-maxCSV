import { app } from "../../../scripts/app.js";

// Code largely inspired by FILL NODES, credit to the author: https://github.com/filliptm/ComfyUI_Fill-Nodes

app.registerExtension({
    name: "Comfy.EZ_Tag_Loader",
    async nodeCreated(node) {
        if (node.comfyClass === "EZ_Tag_Loader") {
            addTagBrowserUI(node);
        }
    }
});

async function addTagBrowserUI(node) {
    // Tweakable variables
    const CLICK_Y_OFFSET = 0;
    const CLICK_X_OFFSET = -2;

    const tagsFileWidget = node.widgets.find(w => w.name === "tags_file");
    const selectedTagsWidget = node.widgets.find(w => w.name === "selected_tags");
    const selectionTypeWidget = node.widgets.find(w => w.name === "selection_type");
    const filterTextWidget = node.widgets.find(w => w.name === "filter_text");

    if (!tagsFileWidget || !selectedTagsWidget || !selectionTypeWidget || !filterTextWidget) {
        console.error("Required widgets not found:", { tagsFileWidget, selectedTagsWidget, selectionTypeWidget, filterTextWidget });
        return;
    }

    tagsFileWidget.hidden = false;
    selectedTagsWidget.hidden = true;
    selectionTypeWidget.hidden = false;
    filterTextWidget.hidden = false;

    const MIN_WIDTH = 310;
    const MIN_HEIGHT = 340;
    const TOP_PADDING = 190;
    const BOTTOM_PADDING = 5;
    const BOTTOM_SKIP = 10;
    const TOP_BAR_HEIGHT = 0;
    const TAG_HEIGHT = 28;
    const TAG_PADDING = 5;
    const EXTRA_TAG_PADDING = 2;
    const SCROLLBAR_WIDTH = 13;
    const MIN_COLUMN_WIDTH = 150; // Minimum width for a column
    const TEXT_PADDING = 10; // Padding for text within tag
    const PREVIEW_PADDING = 20; // Padding for preview text
    const PREVIEW_SKIP = 152; // Skip for preview text
    const BORDER_RADIUS = 0;
    const SELECTION_BORDER_RADIUS = 0;
    const SELECTION_BORDER_PADDING = 0;
    const ELLIPSIS = "...";

    const COLORS = {
        background: "#1e1e1e",
        topBar: "#252526",
        tag: "#2d2d30",
        tagHover: "#3e3e42",
        tagSelected: "#0e639c",
        text: "#ffffff",
        scrollbar: "#3e3e42",
        scrollbarHover: "#505050",
        divider: "#4f0074",
        dividerHover: "#16727c"
    };

    let currentFile = null;
    let filterText = filterTextWidget.value;
    let selectedTags = new Set();
    let tags = [];
    let scrollOffset = 0;
    let isDragging = false;
    let scrollStartY = 0;
    let scrollStartOffset = 0;

    async function updateTags() {
        try {
            const response = await fetch('/ez_tag_browser/get_directory_structure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: currentFile, filter: filterText })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData.error);
                return;
            }

            const data = await response.json();
            if (!data.tags) {
                console.error("Invalid response format:", data);
                return;
            }

            tags = data.tags;
            node.setDirtyCanvas(true);
        } catch (error) {
            console.error("Error updating tags:", error);
        }
    }

    async function fetchFileInfo(relativePath) {
        try {
            const response = await fetch('/ez_tag_browser/get_file_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ relative_path: relativePath })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData.error);
                return null;
            }

            const result = await response.json();
            return result.full_path || null;
        } catch (error) {
            console.error("Error fetching file info:", error);
            return null;
        }
    }

    function updateSelectedTags(tag) {
        if (selectionTypeWidget.value === "multiple" || selectionTypeWidget.value === "random") {
            if (selectedTags.has(tag)) {
                selectedTags.delete(tag);
            } else {
                selectedTags.add(tag);
            }
        } else {
            selectedTags.clear();
            selectedTags.add(tag);
        }
        
        const selectedTagsString = Array.from(selectedTags).join(", ");
        selectedTagsWidget.value = selectedTagsString;
        node.setDirtyCanvas(true);
    }

    function drawPreviewText(ctx, text) {
        ctx.fillStyle = COLORS.text;
        ctx.font = "12px Arial";
        
        // Calculate available width for text
        const maxWidth = node.size[0] - PREVIEW_PADDING * 2;
        
        let displayText = text;
        
        // For random mode, show tag count
        if (selectionTypeWidget.value === "random") {
            const tagCount = selectedTags.size > 0 ? selectedTags.size : tags.length;
            displayText = `selecting from ${tagCount} tags`;
        } else {
            // Measure text width for other modes
            const textMetrics = ctx.measureText(text);
            
            // If text is too long, truncate it
            if (textMetrics.width > maxWidth) {
                let truncatedText = text;
                while (ctx.measureText(truncatedText + ELLIPSIS).width > maxWidth && truncatedText.length > 0) {
                    truncatedText = truncatedText.slice(0, -1);
                }
                displayText = truncatedText + ELLIPSIS;
            }
        }
        
        // Draw the text
            ctx.fillText(displayText, PREVIEW_PADDING, PREVIEW_SKIP);
    }

    const refreshButton = node.addWidget("button", "Refresh / Clear", null, () => {
        selectedTags.clear();
        selectedTagsWidget.value = "";
        (async () => {
            currentFile = await fetchFileInfo(tagsFileWidget.value);
            if (currentFile) {
                updateTags();
            }
        })();
    });

    tagsFileWidget.callback = () => {
        selectedTags.clear();
        selectedTagsWidget.value = "";
        (async () => {
            currentFile = await fetchFileInfo(tagsFileWidget.value);
            if (currentFile) {
                updateTags();
            }
        })();
    };

    filterTextWidget.callback = () => {
        filterText = filterTextWidget.value;
        updateTags();
    };

    selectionTypeWidget.callback = () => {
        selectedTags.clear();
        selectedTagsWidget.value = "";
        node.setDirtyCanvas(true);
    };

    node.onDrawBackground = function(ctx) {
        if (!this.flags.collapsed) {
            const pos = TOP_PADDING - TOP_BAR_HEIGHT;
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, pos, this.size[0], this.size[1] - pos - BOTTOM_SKIP);

            // Draw top bar
            ctx.fillStyle = COLORS.topBar;
            ctx.fillRect(0, pos, this.size[0], TOP_BAR_HEIGHT);

            // Draw selected tags preview
            drawPreviewText(ctx, selectedTagsWidget.value);

            ctx.save();
            ctx.beginPath();
            ctx.rect(0, TOP_PADDING, this.size[0] - SCROLLBAR_WIDTH, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP);
            ctx.clip();
            drawTags(ctx, 0, TOP_PADDING - scrollOffset, this.size[0] - SCROLLBAR_WIDTH - 10, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP);
            ctx.restore();

            // Draw scrollbar
            drawScrollbar(ctx, this.size[0] - SCROLLBAR_WIDTH, TOP_PADDING, SCROLLBAR_WIDTH, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP, scrollOffset, getTotalTagsHeight());
        }
    };

    function drawRoundedRect(ctx, x, y, width, height, radius, color) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
    }

    function drawScrollbar(ctx, x, y, width, height, offset, totalHeight) {
        drawRoundedRect(ctx, x, y, width, height, width / 2, COLORS.scrollbar);

        const visibleHeight = height;
        const scrollHeight = Math.max(height * (visibleHeight / totalHeight), 20);
        const maxOffset = Math.max(0, totalHeight - visibleHeight);
        const scrollY = y + (offset / maxOffset) * (height - scrollHeight);

        drawRoundedRect(ctx, x, scrollY, width, scrollHeight, width / 2, COLORS.scrollbarHover);
    }

    function getTotalTagsHeight() {
        const columns = Math.max(2, Math.floor((node.size[0] - SCROLLBAR_WIDTH) / MIN_COLUMN_WIDTH));
        const rows = Math.ceil(tags.length / columns);
        return rows * (TAG_HEIGHT + TAG_PADDING);
    }

    function drawTags(ctx, x, y, width, height) {
        ctx.fillStyle = COLORS.background;
        ctx.fillRect(x, y, width, height);

        const columns = Math.max(2, Math.floor((node.size[0] - SCROLLBAR_WIDTH) / MIN_COLUMN_WIDTH));
        const columnWidth = (width - TAG_PADDING * (columns + 1)) / columns;
        const rows = Math.ceil(tags.length / columns);

        const visibleHeight = height;
        const startRow = Math.floor(scrollOffset / (TAG_HEIGHT + TAG_PADDING));
        const endRow = Math.min(rows, startRow + Math.ceil(visibleHeight / (TAG_HEIGHT + TAG_PADDING))+2);

        for (let row = startRow; row < endRow; row++) {
            for (let col = 0; col < columns; col++) {
                const tagIndex = row * columns + col;
                if (tagIndex >= tags.length) break;

                const tag = tags[tagIndex];
                const xPos = x + EXTRA_TAG_PADDING + TAG_PADDING + col * (columnWidth + TAG_PADDING);
                const yPos = y + EXTRA_TAG_PADDING + row * (TAG_HEIGHT + TAG_PADDING) + TAG_PADDING;

                // Draw tag background
                const bgColor = selectedTags.has(tag) ? COLORS.tagSelected : COLORS.tag;
                drawRoundedRect(ctx, xPos, yPos, columnWidth, TAG_HEIGHT, BORDER_RADIUS, bgColor);

                // Draw tag text with truncation
                ctx.fillStyle = COLORS.text;
                ctx.font = "12px Arial";
                
                // Calculate available width for text
                const maxTextWidth = columnWidth - TEXT_PADDING * 2;
                
                // Measure text width
                const textMetrics = ctx.measureText(tag);
                let displayText = tag;
                
                // If text is too long, truncate it
                if (textMetrics.width > maxTextWidth) {
                    let truncatedText = tag;
                    while (ctx.measureText(truncatedText + ELLIPSIS).width > maxTextWidth && truncatedText.length > 0) {
                        truncatedText = truncatedText.slice(0, -1);
                    }
                    displayText = truncatedText + ELLIPSIS;
                }
                
                // Draw the text
                ctx.fillText(displayText, xPos + TEXT_PADDING, yPos + TAG_HEIGHT / 2 + 4);
            }
        }
    }

    node.onMouseDown = function(event) {
        const pos = TOP_PADDING - TOP_BAR_HEIGHT;
        const localY = event.canvasY - this.pos[1] - pos + CLICK_Y_OFFSET;
        const localX = event.canvasX - this.pos[0] + CLICK_X_OFFSET;

        if (localY < 0 || localY > this.size[1] || localX < 0 || localX > this.size[0]) {
            return false;
        }

        if (localY > TOP_BAR_HEIGHT && localY < this.size[1] - pos - 10) {
            if (localX >= 0 && localX < this.size[0] - SCROLLBAR_WIDTH) {
                // Calculate which tag was clicked
                const columns = Math.max(2, Math.floor((this.size[0] - SCROLLBAR_WIDTH) / MIN_COLUMN_WIDTH));
                const column = Math.floor(localX / ((this.size[0] - SCROLLBAR_WIDTH) / columns));
                const row = Math.floor((localY - TOP_BAR_HEIGHT + scrollOffset) / (TAG_HEIGHT + TAG_PADDING));
                const tagIndex = row * columns + column;
                
                if (tagIndex >= 0 && tagIndex < tags.length) {
                    updateSelectedTags(tags[tagIndex]);
                }
                return true;
            } else if (localX >= this.size[0] - SCROLLBAR_WIDTH) {
                // Click on scrollbar
                isDragging = true;
                scrollStartY = event.canvasY;
                scrollStartOffset = scrollOffset;
                return true;
            }
        }

        return false;
    };

    node.onMouseMove = function(event) {
        const pos = TOP_PADDING - TOP_BAR_HEIGHT;
        const localY = event.canvasY - this.pos[1] - pos + CLICK_Y_OFFSET;
        const localX = event.canvasX - this.pos[0] + CLICK_X_OFFSET;

        if (isDragging) {
            const totalHeight = getTotalTagsHeight();
            const visibleHeight = this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP;
            const maxOffset = Math.max(0, totalHeight - visibleHeight);
            const scrollMove = (event.canvasY - scrollStartY) * (totalHeight / visibleHeight);
            scrollOffset = Math.max(0, Math.min(maxOffset, scrollStartOffset + scrollMove));
            this.setDirtyCanvas(true);
            return true;
        }

        return false;
    };

    node.onMouseUp = function(event) {
        isDragging = false;
        document.body.style.cursor = 'default';
        return false;
    };

    function updateNodeSize() {
        const width = Math.max(MIN_WIDTH, node.size[0]);
        const height = Math.max(MIN_HEIGHT, node.size[1]);
        node.size[0] = width;
        node.size[1] = height;
    }

    node.onResize = function() {
        updateNodeSize();
        this.setDirtyCanvas(true);
    };

    // Initialize
    setTimeout(async () => {
        currentFile = await fetchFileInfo(tagsFileWidget.value);
        if (currentFile) {
            updateTags();
        }
        updateNodeSize();
    }, 0);
}