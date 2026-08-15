var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);

// main.ts
var main_exports = {};
__export(main_exports, {
  default: () => ReadingAssociationPlugin
});
module.exports = __toCommonJS(main_exports);
var import_obsidian = require("obsidian");
var VIEW_TYPE = "reading-association-view";
var ASSOCIATION_HEADING = "## \u9605\u8BFB\u8054\u60F3";
function emptyDraft() {
  return {
    sourceBook: "",
    excerpt: "",
    sourceLine: null,
    relatedFilePath: "",
    relatedLine: null,
    relatedPreview: "",
    relatedKind: "",
    originalThought: "",
    aiDiscussion: "",
    currentInsight: "",
    title: "",
    needsVerification: false
  };
}
function localDate() {
  const now = /* @__PURE__ */ new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
function cleanPreview(value, limit = 56) {
  const clean = value.replace(/^#{1,6}\s+/, "").replace(/^[-*>\s]+/, "").replace(/\s+/g, " ").trim();
  return clean.length > limit ? `${clean.slice(0, limit)}\u2026` : clean;
}
function asCalloutBody(value) {
  const lines = value.trim().split("\n");
  return lines.map((line) => `> ${line}`).join("\n");
}
function buildMarkdown(draft, sourceLink, relatedLink) {
  const discussion = draft.aiDiscussion.trim() || "\u672C\u6B21\u672A\u4F7F\u7528 AI \u8BA8\u8BBA\u3002";
  const evidence = draft.needsVerification ? "- [ ] \u5F85\u6838\u5BF9\u539F\u6587" : "\u8BA8\u8BBA\u6027\u5224\u65AD\uFF0C\u5C1A\u672A\u8FDB\u884C\u539F\u6587\u6838\u5BF9";
  return [
    `### ${localDate()} \xB7 ${draft.title.trim()}`,
    "",
    `**\u6765\u6E90\u7247\u6BB5**\uFF1A${sourceLink}`,
    "",
    "> [!quote] \u5F53\u524D\u9605\u8BFB\u7247\u6BB5",
    asCalloutBody(draft.excerpt || "\u672A\u8BB0\u5F55\u5177\u4F53\u7247\u6BB5"),
    "",
    `**\u5173\u8054\u7247\u6BB5**\uFF1A${relatedLink}`,
    "",
    "#### \u6211\u7684\u539F\u59CB\u8054\u60F3",
    "",
    draft.originalThought.trim(),
    "",
    "#### AI \u8BA8\u8BBA",
    "",
    discussion,
    "",
    "#### \u5F53\u524D\u8BA4\u8BC6",
    "",
    draft.currentInsight.trim(),
    "",
    `**\u8BC1\u636E\u72B6\u6001**\uFF1A${evidence}`
  ].join("\n");
}
function parseBlocks(content) {
  var _a;
  const lines = content.split("\n");
  const blocks = [];
  let paragraphStart = null;
  let inCode = false;
  let frontmatterEnd = -1;
  if (((_a = lines[0]) == null ? void 0 : _a.trim()) === "---") {
    frontmatterEnd = lines.findIndex((line, index) => index > 0 && line.trim() === "---");
  }
  const flushParagraph = (endLine) => {
    if (paragraphStart === null) return;
    const text = lines.slice(paragraphStart, endLine + 1).join("\n").trim();
    if (text && !/^\^[A-Za-z0-9_-]+$/.test(text)) {
      blocks.push({ line: paragraphStart, endLine, text, kind: "paragraph" });
    }
    paragraphStart = null;
  };
  lines.forEach((line, index) => {
    if (index <= frontmatterEnd) return;
    if (/^```/.test(line.trim())) {
      flushParagraph(index - 1);
      inCode = !inCode;
      return;
    }
    if (inCode) return;
    const heading = /^(#{1,6})\s+(.+?)\s*$/.exec(line);
    if (heading) {
      flushParagraph(index - 1);
      blocks.push({ line: index, endLine: index, text: heading[2], kind: "heading" });
      return;
    }
    if (!line.trim()) {
      flushParagraph(index - 1);
      return;
    }
    if (paragraphStart === null) paragraphStart = index;
  });
  flushParagraph(lines.length - 1);
  return blocks;
}
var NoteSuggestModal = class extends import_obsidian.FuzzySuggestModal {
  constructor(app, files, onChoose) {
    super(app);
    __publicField(this, "files", files);
    __publicField(this, "onChoose", onChoose);
    this.setPlaceholder("\u9009\u62E9\u5173\u8054\u7B14\u8BB0\u2026");
  }
  getItems() {
    return this.files;
  }
  getItemText(file) {
    return file.path;
  }
  onChooseItem(file) {
    this.onChoose(file);
  }
};
var BlockSuggestModal = class extends import_obsidian.FuzzySuggestModal {
  constructor(app, blocks, onChoose) {
    super(app);
    __publicField(this, "blocks", blocks);
    __publicField(this, "onChoose", onChoose);
    this.setPlaceholder("\u641C\u7D22\u5E76\u9009\u62E9\u5177\u4F53\u6807\u9898\u6216\u6BB5\u843D\u2026");
  }
  getItems() {
    return this.blocks;
  }
  getItemText(block) {
    const type = block.kind === "heading" ? "\u6807\u9898" : "\u6BB5\u843D";
    return `${type} \xB7 ${cleanPreview(block.text, 100)}`;
  }
  onChooseItem(block) {
    this.onChoose(block);
  }
};
function insertAssociation(content, entry) {
  const headingPattern = /^## 阅读联想\s*$/m;
  const match = headingPattern.exec(content);
  if (!match) {
    return `${content.trimEnd()}

${ASSOCIATION_HEADING}

${entry}
`;
  }
  const insertAt = match.index + match[0].length;
  const before = content.slice(0, insertAt);
  const after = content.slice(insertAt).replace(/^\s*/, "");
  return `${before}

${entry}
${after ? `
${after}` : ""}`;
}
function findBlock(content, line, excerpt) {
  const blocks = parseBlocks(content);
  const selected = excerpt.trim();
  const atLine = line === null ? null : blocks.find((block) => block.line <= line && block.endLine >= line && (!selected || block.text.includes(selected)));
  if (atLine) return atLine;
  const matches = blocks.filter((block) => selected && block.text.includes(selected));
  return matches.length === 1 ? matches[0] : null;
}
function createBlockId() {
  const time = Date.now().toString(36);
  const random = Math.random().toString(36).slice(2, 7);
  return `ra-${time}-${random}`;
}
function linkPath(file) {
  return file.path.replace(/\.md$/, "");
}
function linkAlias(value) {
  return cleanPreview(value).replace(/[\]|]/g, "");
}
function makePreciseLink(file, subpath, preview) {
  return `[[${linkPath(file)}${subpath}|${linkAlias(preview)}]]`;
}
function ensureBlockReference(content, candidate) {
  var _a, _b, _c;
  if (candidate.kind === "heading") {
    return { content, subpath: `#${candidate.text}` };
  }
  const existingId = (_a = /(?:^|\s)\^([A-Za-z0-9_-]+)\s*$/m.exec(candidate.text)) == null ? void 0 : _a[1];
  if (existingId) return { content, subpath: `#^${existingId}` };
  const id = createBlockId();
  const lines = content.split("\n");
  const firstLine = (_c = (_b = lines[candidate.line]) == null ? void 0 : _b.trim()) != null ? _c : "";
  const separateLine = /^(?:[-*+]\s|\d+[.)]\s|>|\|)/.test(firstLine);
  if (separateLine) {
    lines.splice(candidate.endLine + 1, 0, `^${id}`);
  } else {
    lines[candidate.endLine] = `${lines[candidate.endLine].trimEnd()} ^${id}`;
  }
  return { content: lines.join("\n"), subpath: `#^${id}` };
}
function addDirectRelation(content, sourceSubpath, relatedLink) {
  if (content.includes(`\u5173\u8054\u89C2\u70B9\uFF1A${relatedLink}`)) return content;
  const lines = content.split("\n");
  let insertionLine = -1;
  if (sourceSubpath.startsWith("#^")) {
    const id = sourceSubpath.slice(2);
    insertionLine = lines.findIndex((line) => new RegExp(`(?:^|\\s)\\^${id}\\s*$`).test(line));
  } else if (sourceSubpath.startsWith("#")) {
    const heading = sourceSubpath.slice(1);
    insertionLine = lines.findIndex((line) => /^#{1,6}\s+/.test(line) && line.replace(/^#{1,6}\s+/, "").trim() === heading);
  }
  if (insertionLine < 0) return content;
  lines.splice(insertionLine + 1, 0, "", `\u5173\u8054\u89C2\u70B9\uFF1A${relatedLink}`, "");
  return lines.join("\n");
}
var ReadingAssociationView = class extends import_obsidian.ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    __publicField(this, "plugin", plugin);
    __publicField(this, "stage", "capture");
    __publicField(this, "draft", emptyDraft());
    __publicField(this, "targetFile", null);
  }
  getViewType() {
    return VIEW_TYPE;
  }
  getDisplayText() {
    return "\u9605\u8BFB\u8054\u60F3";
  }
  getIcon() {
    return "book-open-text";
  }
  async onOpen() {
    this.restoreTargetIfMissing();
    this.render();
  }
  start(file, selection, line) {
    var _a;
    this.targetFile = file;
    this.stage = "capture";
    this.draft = emptyDraft();
    this.draft.sourceBook = (_a = file == null ? void 0 : file.basename) != null ? _a : "";
    this.draft.excerpt = selection.trim();
    this.draft.sourceLine = line;
    this.render();
  }
  restoreTargetIfMissing() {
    var _a, _b;
    if (this.targetFile) return;
    const context = this.plugin.getReadingContext();
    this.targetFile = context.file;
    this.draft.sourceBook = (_b = (_a = context.file) == null ? void 0 : _a.basename) != null ? _b : "";
    if (!this.draft.excerpt) this.draft.excerpt = context.selection;
    if (this.draft.sourceLine === null) this.draft.sourceLine = context.line;
  }
  render() {
    const container = this.containerEl.children[1];
    container.empty();
    container.addClass("reading-association-view");
    const header = container.createDiv({ cls: "ra-header" });
    const titleRow = header.createDiv({ cls: "ra-title-row" });
    const icon = titleRow.createSpan({ cls: "ra-icon" });
    (0, import_obsidian.setIcon)(icon, "book-open-text");
    titleRow.createEl("h2", { text: "\u9605\u8BFB\u8054\u60F3" });
    header.createEl("p", {
      text: "\u5148\u4FDD\u7559\u4F60\u7684\u5224\u65AD\uFF0C\u518D\u8BA9 AI \u53C2\u4E0E\u8BA8\u8BBA\u3002",
      cls: "ra-subtitle"
    });
    this.renderProgress(container);
    if (this.stage === "capture") this.renderCapture(container);
    if (this.stage === "discuss") this.renderDiscuss(container);
    if (this.stage === "distill") this.renderDistill(container);
    if (this.stage === "saved") this.renderSaved(container);
  }
  renderProgress(parent) {
    const stages = [
      { id: "capture", label: "\u8054\u60F3" },
      { id: "discuss", label: "\u8BA8\u8BBA" },
      { id: "distill", label: "\u6C89\u6DC0" }
    ];
    const order = ["capture", "discuss", "distill", "saved"];
    const current = order.indexOf(this.stage);
    const progress = parent.createDiv({ cls: "ra-progress" });
    stages.forEach((item, index) => {
      const step = progress.createDiv({ cls: "ra-progress-step" });
      if (index <= current) step.addClass("is-active");
      step.createSpan({ text: String(index + 1), cls: "ra-progress-number" });
      step.createSpan({ text: item.label });
    });
  }
  renderCapture(parent) {
    var _a, _b;
    const target = parent.createDiv({ cls: "ra-target" });
    target.createSpan({ text: "\u5199\u5165\u4F4D\u7F6E" });
    target.createEl("strong", {
      text: (_b = (_a = this.targetFile) == null ? void 0 : _a.path) != null ? _b : "\u672A\u627E\u5230\u5F53\u524D Markdown \u7B14\u8BB0"
    });
    if (!this.targetFile) {
      parent.createDiv({
        text: "\u8BF7\u5148\u6253\u5F00\u4E00\u672C\u4E66\u7684 Markdown \u7B14\u8BB0\uFF0C\u518D\u91CD\u65B0\u8FD0\u884C\u201C\u5F00\u59CB\u4E00\u6B21\u9605\u8BFB\u8054\u60F3\u201D\u3002",
        cls: "ra-warning"
      });
    }
    this.addTextarea(parent, "\u5F53\u524D\u9605\u8BFB\u7247\u6BB5", this.draft.excerpt, (value) => {
      this.draft.excerpt = value;
    }, "\u8BF7\u4ECE\u5F53\u524D\u7B14\u8BB0\u4E2D\u9009\u4E2D\u6587\u5B57\uFF1B\u4FDD\u5B58\u65F6\u4F1A\u7ED9\u6240\u5728\u6BB5\u843D\u5EFA\u7ACB\u7A33\u5B9A\u5757\u5F15\u7528\u3002", 5);
    const relatedField = parent.createDiv({ cls: "ra-field" });
    relatedField.createEl("label", { text: "\u5173\u8054\u7B14\u8BB0\u4E2D\u7684\u5177\u4F53\u6807\u9898\u6216\u6BB5\u843D" });
    if (this.draft.relatedFilePath) {
      const selected = relatedField.createDiv({ cls: "ra-selected-block" });
      selected.createEl("strong", { text: this.draft.relatedFilePath });
      selected.createEl("span", { text: cleanPreview(this.draft.relatedPreview, 100) });
    }
    const choose = relatedField.createEl("button", {
      text: this.draft.relatedFilePath ? "\u91CD\u65B0\u9009\u62E9\u5173\u8054\u7247\u6BB5" : "\u9009\u62E9\u5173\u8054\u7B14\u8BB0\u548C\u5177\u4F53\u7247\u6BB5"
    });
    choose.addEventListener("click", () => {
      this.plugin.pickRelatedBlock(this.targetFile, (file, block) => {
        this.draft.relatedFilePath = file.path;
        this.draft.relatedLine = block.line;
        this.draft.relatedPreview = block.text;
        this.draft.relatedKind = block.kind;
        this.render();
      });
    });
    relatedField.createEl("small", {
      text: "\u4FDD\u5B58\u540E\uFF0C\u5F53\u524D\u6BB5\u843D\u4F1A\u76F4\u63A5\u94FE\u63A5\u5230\u8FD9\u91CC\uFF1B\u4E0D\u4F1A\u521B\u5EFA\u89C2\u70B9\u6587\u6863\u3002"
    });
    this.addTextarea(parent, "\u6211\u7684\u539F\u59CB\u8054\u60F3", this.draft.originalThought, (value) => {
      this.draft.originalThought = value;
    }, "\u5148\u5199\u4E0B\u4F60\u8BA4\u4E3A\u5B83\u4EEC\u4E3A\u4EC0\u4E48\u6709\u5173\uFF0C\u4E0D\u5FC5\u5B9A\u4F4D\u539F\u6587\u3002", 7);
    const actions = parent.createDiv({ cls: "ra-actions" });
    const next = actions.createEl("button", { text: "\u5E26\u7740\u6211\u7684\u5224\u65AD\u5F00\u59CB\u8BA8\u8BBA", cls: "mod-cta" });
    next.addEventListener("click", () => {
      this.restoreTargetIfMissing();
      if (!this.targetFile) {
        new import_obsidian.Notice("\u8BF7\u5148\u6253\u5F00\u4E00\u672C\u4E66\u7684 Markdown \u7B14\u8BB0");
        return;
      }
      if (!this.draft.originalThought.trim()) {
        new import_obsidian.Notice("\u8BF7\u5148\u5199\u4E0B\u4F60\u7684\u539F\u59CB\u8054\u60F3");
        return;
      }
      if (!this.draft.excerpt.trim() || this.draft.sourceLine === null) {
        new import_obsidian.Notice("\u8BF7\u5148\u5728\u5F53\u524D\u7B14\u8BB0\u4E2D\u9009\u4E2D\u4E00\u4E2A\u771F\u5B9E\u7247\u6BB5\uFF0C\u518D\u5F00\u59CB\u9605\u8BFB\u8054\u60F3");
        return;
      }
      if (!this.draft.relatedFilePath || this.draft.relatedLine === null) {
        new import_obsidian.Notice("\u8BF7\u9009\u62E9\u5173\u8054\u7B14\u8BB0\u4E2D\u7684\u5177\u4F53\u6807\u9898\u6216\u6BB5\u843D");
        return;
      }
      this.stage = "discuss";
      this.render();
    });
  }
  renderDiscuss(parent) {
    const status = parent.createDiv({ cls: "ra-mode" });
    status.createSpan({ text: "\u4EBA\u5DE5 AI \u534F\u4F5C\u6A21\u5F0F" });
    status.createSpan({ text: "\u4E0D\u68C0\u7D22\u65E7\u4E66" });
    const summary = parent.createDiv({ cls: "ra-summary" });
    summary.createEl("strong", { text: "\u4F60\u7684\u539F\u59CB\u5224\u65AD" });
    summary.createEl("p", { text: this.draft.originalThought });
    parent.createEl("p", {
      text: "\u590D\u5236\u4E0B\u9762\u7684\u4E0A\u4E0B\u6587\u53D1\u7ED9 Codex\u3002\u8BA8\u8BBA\u5B8C\u6210\u540E\uFF0C\u628A\u4F60\u8BA4\u4E3A\u6709\u4EF7\u503C\u7684 AI \u56DE\u590D\u8D34\u56DE\u6765\u3002",
      cls: "ra-help"
    });
    const copyButton = parent.createEl("button", { text: "\u590D\u5236\u8BA8\u8BBA\u4E0A\u4E0B\u6587", cls: "mod-cta" });
    copyButton.addEventListener("click", async () => {
      await navigator.clipboard.writeText(this.buildDiscussionPrompt());
      copyButton.setText("\u5DF2\u590D\u5236\uFF0C\u53EF\u4EE5\u53D1\u7ED9 Codex");
      new import_obsidian.Notice("\u8BA8\u8BBA\u4E0A\u4E0B\u6587\u5DF2\u590D\u5236");
    });
    this.addTextarea(parent, "AI \u8BA8\u8BBA\u8BB0\u5F55", this.draft.aiDiscussion, (value) => {
      this.draft.aiDiscussion = value;
    }, "\u8BA8\u8BBA\u540E\u518D\u7C98\u8D34\uFF1B\u4E5F\u53EF\u4EE5\u7559\u7A7A\u3002", 8);
    const verifyRow = parent.createEl("label", { cls: "ra-checkbox" });
    const verify = verifyRow.createEl("input", { type: "checkbox" });
    verify.checked = this.draft.needsVerification;
    verify.addEventListener("change", () => {
      this.draft.needsVerification = verify.checked;
    });
    verifyRow.createSpan({ text: "\u8FD9\u90E8\u5206\u4EE5\u540E\u9700\u8981\u6838\u5BF9\u539F\u6587" });
    const actions = parent.createDiv({ cls: "ra-actions" });
    const back = actions.createEl("button", { text: "\u8FD4\u56DE\u4FEE\u6539" });
    back.addEventListener("click", () => {
      this.stage = "capture";
      this.render();
    });
    const next = actions.createEl("button", { text: "\u5F62\u6210\u5F53\u524D\u8BA4\u8BC6", cls: "mod-cta" });
    next.addEventListener("click", () => {
      var _a, _b;
      this.stage = "distill";
      if (!this.draft.title) {
        const relatedName = (_b = (_a = this.draft.relatedFilePath.split("/").pop()) == null ? void 0 : _a.replace(/\.md$/, "")) != null ? _b : "\u53E6\u4E00\u89C2\u70B9";
        this.draft.title = this.draft.relatedFilePath ? `\u4E0E${relatedName.replace(/[《》]/g, "")}\u7684\u8054\u7CFB` : "\u4E00\u6B21\u8DE8\u4E66\u8054\u60F3";
      }
      this.render();
    });
  }
  renderDistill(parent) {
    parent.createEl("p", {
      text: "\u53EA\u6709\u4F60\u786E\u8BA4\u540E\u7684\u5185\u5BB9\u624D\u4F1A\u5199\u5165\u4E66\u7C4D\u7B14\u8BB0\u3002AI \u56DE\u590D\u548C\u4F60\u7684\u8BA4\u8BC6\u4F1A\u5206\u5F00\u4FDD\u5B58\u3002",
      cls: "ra-help"
    });
    this.addInput(parent, "\u8054\u60F3\u6807\u9898", this.draft.title, (value) => {
      this.draft.title = value;
    });
    this.addTextarea(parent, "\u8BA8\u8BBA\u540E\u5F62\u6210\u7684\u5F53\u524D\u8BA4\u8BC6", this.draft.currentInsight, (value) => {
      this.draft.currentInsight = value;
    }, "\u7528\u4F60\u81EA\u5DF1\u7684\u8BDD\u5199\u4E0B\u73B0\u5728\u7684\u5224\u65AD\u3001\u9002\u7528\u8FB9\u754C\u6216\u4ECD\u7136\u4E0D\u786E\u5B9A\u7684\u5730\u65B9\u3002", 8);
    const preview = parent.createEl("details", { cls: "ra-preview" });
    preview.createEl("summary", { text: "\u9884\u89C8\u5199\u5165\u5185\u5BB9" });
    preview.createEl("pre", {
      text: buildMarkdown(
        this.draft,
        "[[\u5F53\u524D\u7B14\u8BB0#^\u7CBE\u786E\u6BB5\u843D|\u5F53\u524D\u9605\u8BFB\u7247\u6BB5]]",
        `[[${this.draft.relatedFilePath.replace(/\.md$/, "")}#^\u7CBE\u786E\u6BB5\u843D|${cleanPreview(this.draft.relatedPreview)}]]`
      )
    });
    const actions = parent.createDiv({ cls: "ra-actions" });
    const back = actions.createEl("button", { text: "\u8FD4\u56DE\u8BA8\u8BBA" });
    back.addEventListener("click", () => {
      this.stage = "discuss";
      this.render();
    });
    const save = actions.createEl("button", { text: "\u5199\u5165\u5F53\u524D\u4E66\u7C4D\u7B14\u8BB0", cls: "mod-cta" });
    save.addEventListener("click", async () => {
      if (!this.draft.title.trim() || !this.draft.currentInsight.trim()) {
        new import_obsidian.Notice("\u8BF7\u586B\u5199\u8054\u60F3\u6807\u9898\u548C\u5F53\u524D\u8BA4\u8BC6");
        return;
      }
      if (!this.targetFile) {
        new import_obsidian.Notice("\u76EE\u6807\u7B14\u8BB0\u4E0D\u5B58\u5728");
        return;
      }
      try {
        await this.plugin.savePreciseAssociation(this.targetFile, this.draft);
        this.stage = "saved";
        this.render();
      } catch (error) {
        const message = error instanceof Error ? error.message : "\u4FDD\u5B58\u5931\u8D25";
        new import_obsidian.Notice(message);
      }
    });
  }
  renderSaved(parent) {
    var _a, _b;
    const success = parent.createDiv({ cls: "ra-success" });
    const icon = success.createSpan({ cls: "ra-success-icon" });
    (0, import_obsidian.setIcon)(icon, "check");
    success.createEl("h3", { text: "\u5DF2\u7ECF\u6C89\u6DC0\u5230\u4E66\u7C4D\u7B14\u8BB0" });
    success.createEl("p", {
      text: "\u8FD9\u6B21\u53EA\u589E\u52A0\u4E86\u4E00\u6761\u9605\u8BFB\u8054\u60F3\uFF0C\u6CA1\u6709\u521B\u5EFA\u65B0\u7684\u788E\u7247\u6587\u4EF6\u3002"
    });
    const target = success.createEl("button", {
      text: (_b = (_a = this.targetFile) == null ? void 0 : _a.path) != null ? _b : "\u67E5\u770B\u76EE\u6807\u7B14\u8BB0",
      cls: "ra-file-button"
    });
    target.addEventListener("click", async () => {
      if (this.targetFile) await this.app.workspace.getLeaf(false).openFile(this.targetFile);
    });
    const restart = parent.createEl("button", { text: "\u5F00\u59CB\u4E0B\u4E00\u6B21\u8054\u60F3", cls: "mod-cta" });
    restart.addEventListener("click", () => {
      var _a2, _b2, _c;
      const active = this.app.workspace.getActiveViewOfType(import_obsidian.MarkdownView);
      this.start(
        (_a2 = active == null ? void 0 : active.file) != null ? _a2 : this.targetFile,
        (_b2 = active == null ? void 0 : active.editor.getSelection()) != null ? _b2 : "",
        (_c = active == null ? void 0 : active.editor.getCursor("from").line) != null ? _c : null
      );
    });
  }
  addInput(parent, labelText, value, onChange, placeholder = "") {
    const field = parent.createDiv({ cls: "ra-field" });
    field.createEl("label", { text: labelText });
    const input = field.createEl("input", { type: "text", placeholder });
    input.value = value;
    input.addEventListener("input", () => onChange(input.value));
  }
  addTextarea(parent, labelText, value, onChange, help, rows) {
    const field = parent.createDiv({ cls: "ra-field" });
    field.createEl("label", { text: labelText });
    const textarea = field.createEl("textarea", { attr: { rows: String(rows) } });
    textarea.value = value;
    textarea.addEventListener("input", () => onChange(textarea.value));
    field.createEl("small", { text: help });
  }
  buildDiscussionPrompt() {
    return [
      "\u6211\u6B63\u5728\u8FDB\u884C\u4E00\u6B21\u9605\u8BFB\u8054\u60F3\u8BA8\u8BBA\u3002\u8BF7\u9075\u5B88\u4EE5\u4E0B\u89C4\u5219\uFF1A",
      "1. \u5148\u7406\u89E3\u5E76\u590D\u8FF0\u6211\u7684\u5224\u65AD\uFF0C\u4E0D\u8981\u4E3B\u52A8\u641C\u7D22\u6216\u63A8\u8350\u5176\u4ED6\u4E66\u7C4D\u3002",
      "2. \u901A\u8FC7\u7B80\u77ED\u63D0\u95EE\u5E2E\u52A9\u6211\u8BF4\u6E05\u695A\u8FD9\u79CD\u8054\u7CFB\uFF0C\u6BCF\u6B21\u4F18\u5148\u63A8\u8FDB\u4E00\u4E2A\u95EE\u9898\u3002",
      "3. \u5E2E\u6211\u68C0\u9A8C\u8FD9\u4E2A\u5224\u65AD\u662F\u7C7B\u6BD4\u3001\u89E3\u91CA\u3001\u56E0\u679C\u3001\u51B2\u7A81\u8FD8\u662F\u5176\u4ED6\u5173\u7CFB\u3002",
      "4. \u4E0D\u8981\u4E3A\u4E86\u8D5E\u540C\u800C\u8D5E\u540C\uFF1B\u6307\u51FA\u903B\u8F91\u8DF3\u8DC3\u3001\u9002\u7528\u8FB9\u754C\u548C\u53EF\u80FD\u7684\u53CD\u4F8B\u3002",
      "5. \u9664\u975E\u6211\u660E\u786E\u63D0\u51FA\uFF0C\u5426\u5219\u4E0D\u8981\u68C0\u7D22\u539F\u6587\u3002",
      "",
      `\u5F53\u524D\u4E66\u7C4D\uFF1A${this.draft.sourceBook || "\u672A\u586B\u5199"}`,
      `\u5F53\u524D\u9605\u8BFB\u7247\u6BB5\uFF1A
${this.draft.excerpt || "\u672A\u8BB0\u5F55"}`,
      `\u6211\u60F3\u5230\u7684\u4E66\u6216\u6982\u5FF5\uFF1A${this.draft.relatedFilePath || "\u672A\u586B\u5199"}`,
      `\u5173\u8054\u7684\u5177\u4F53\u7247\u6BB5\uFF1A
${this.draft.relatedPreview || "\u672A\u9009\u62E9"}`,
      `\u6211\u7684\u539F\u59CB\u8054\u60F3\uFF1A
${this.draft.originalThought}`,
      "",
      "\u8BF7\u5148\u7528\u4E00\u4E24\u53E5\u8BDD\u590D\u8FF0\u4F60\u7406\u89E3\u7684\u8054\u7CFB\uFF0C\u7136\u540E\u53EA\u95EE\u6211\u4E00\u4E2A\u6700\u5173\u952E\u7684\u95EE\u9898\u3002"
    ].join("\n");
  }
};
var ReadingAssociationPlugin = class extends import_obsidian.Plugin {
  constructor() {
    super(...arguments);
    __publicField(this, "lastMarkdownFile", null);
  }
  async onload() {
    this.captureCurrentMarkdownFile();
    this.registerEvent(this.app.workspace.on("active-leaf-change", (leaf) => {
      const view = leaf == null ? void 0 : leaf.view;
      if (view instanceof import_obsidian.MarkdownView && view.file) this.lastMarkdownFile = view.file;
    }));
    this.registerEvent(this.app.workspace.on("file-open", (file) => {
      if ((file == null ? void 0 : file.extension) === "md") this.lastMarkdownFile = file;
    }));
    this.registerView(VIEW_TYPE, (leaf) => new ReadingAssociationView(leaf, this));
    this.addRibbonIcon("book-open-text", "\u5F00\u59CB\u4E00\u6B21\u9605\u8BFB\u8054\u60F3", () => {
      void this.startSession();
    });
    this.addCommand({
      id: "start-reading-association",
      name: "\u5F00\u59CB\u4E00\u6B21\u9605\u8BFB\u8054\u60F3",
      callback: () => {
        void this.startSession();
      }
    });
  }
  async onunload() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE);
  }
  async startSession(markdownView) {
    var _a;
    const context = this.getReadingContext(markdownView);
    let leaf = this.app.workspace.getLeavesOfType(VIEW_TYPE)[0];
    if (!leaf) {
      leaf = (_a = this.app.workspace.getRightLeaf(false)) != null ? _a : this.app.workspace.getLeaf("tab");
      await leaf.setViewState({ type: VIEW_TYPE, active: true });
    }
    this.app.workspace.revealLeaf(leaf);
    const view = leaf.view;
    if (view instanceof ReadingAssociationView) view.start(context.file, context.selection, context.line);
  }
  getReadingContext(markdownView) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i;
    const activeEditor = this.app.workspace.activeEditor;
    const recentView = (_a = this.app.workspace.getMostRecentLeaf()) == null ? void 0 : _a.view;
    const recentFile = recentView instanceof import_obsidian.MarkdownView ? recentView.file : null;
    const file = (_f = (_e = (_d = (_c = (_b = markdownView == null ? void 0 : markdownView.file) != null ? _b : activeEditor == null ? void 0 : activeEditor.file) != null ? _c : this.app.workspace.getActiveFile()) != null ? _d : this.lastMarkdownFile) != null ? _e : recentFile) != null ? _f : this.findRootMarkdownFile();
    let editor = (_g = markdownView == null ? void 0 : markdownView.editor) != null ? _g : activeEditor == null ? void 0 : activeEditor.editor;
    let selection = (_h = editor == null ? void 0 : editor.getSelection()) != null ? _h : "";
    let line = selection ? (_i = editor == null ? void 0 : editor.getCursor("from").line) != null ? _i : null : null;
    if (file) this.lastMarkdownFile = file;
    if (!selection && file) {
      const matchingLeaf = this.app.workspace.getLeavesOfType("markdown").find((leaf) => {
        var _a2;
        const view = leaf.view;
        return view instanceof import_obsidian.MarkdownView && ((_a2 = view.file) == null ? void 0 : _a2.path) === file.path;
      });
      if ((matchingLeaf == null ? void 0 : matchingLeaf.view) instanceof import_obsidian.MarkdownView) {
        editor = matchingLeaf.view.editor;
        selection = editor.getSelection();
        line = selection ? editor.getCursor("from").line : null;
      }
    }
    return { file, selection, line };
  }
  pickRelatedBlock(sourceFile, onChoose) {
    const files = this.app.vault.getMarkdownFiles().filter((file) => file.path !== (sourceFile == null ? void 0 : sourceFile.path)).sort((left, right) => {
      const leftReading = left.path.startsWith("04-\u8BFB\u4E66/") ? 0 : 1;
      const rightReading = right.path.startsWith("04-\u8BFB\u4E66/") ? 0 : 1;
      return leftReading - rightReading || left.path.localeCompare(right.path, "zh-CN");
    });
    new NoteSuggestModal(this.app, files, (file) => {
      void this.app.vault.cachedRead(file).then((content) => {
        const blocks = parseBlocks(content);
        if (!blocks.length) {
          new import_obsidian.Notice("\u8FD9\u7BC7\u7B14\u8BB0\u4E2D\u6CA1\u6709\u53EF\u9009\u62E9\u7684\u6807\u9898\u6216\u6BB5\u843D");
          return;
        }
        new BlockSuggestModal(this.app, blocks, (block) => onChoose(file, block)).open();
      });
    }).open();
  }
  captureCurrentMarkdownFile() {
    var _a, _b;
    const activeEditorFile = (_a = this.app.workspace.activeEditor) == null ? void 0 : _a.file;
    const activeFile = this.app.workspace.getActiveFile();
    this.lastMarkdownFile = (_b = activeEditorFile != null ? activeEditorFile : activeFile) != null ? _b : this.findRootMarkdownFile();
  }
  findRootMarkdownFile() {
    let file = null;
    this.app.workspace.iterateRootLeaves((leaf) => {
      if (file) return;
      const view = leaf.view;
      if (view instanceof import_obsidian.MarkdownView && view.file) file = view.file;
    });
    return file;
  }
  async savePreciseAssociation(sourceFile, draft) {
    const related = this.app.vault.getAbstractFileByPath(draft.relatedFilePath);
    if (!(related instanceof import_obsidian.TFile) || related.extension !== "md") {
      throw new Error("\u5173\u8054\u7B14\u8BB0\u4E0D\u5B58\u5728\uFF0C\u8BF7\u91CD\u65B0\u9009\u62E9");
    }
    const sourceOriginal = await this.app.vault.cachedRead(sourceFile);
    const sourceBlock = findBlock(sourceOriginal, draft.sourceLine, draft.excerpt);
    if (!sourceBlock) {
      throw new Error("\u5F53\u524D\u9605\u8BFB\u7247\u6BB5\u5DF2\u53D8\u5316\u6216\u5B58\u5728\u591A\u5904\uFF0C\u65E0\u6CD5\u5EFA\u7ACB\u7CBE\u786E\u94FE\u63A5\uFF0C\u8BF7\u91CD\u65B0\u9009\u4E2D\u6587\u5B57");
    }
    let relatedContent = await this.app.vault.cachedRead(related);
    const relatedBlock = findBlock(relatedContent, draft.relatedLine, draft.relatedPreview);
    if (!relatedBlock) throw new Error("\u65E0\u6CD5\u5B9A\u4F4D\u5173\u8054\u7247\u6BB5\uFF0C\u8BF7\u91CD\u65B0\u9009\u62E9");
    const relatedRef = ensureBlockReference(relatedContent, relatedBlock);
    relatedContent = relatedRef.content;
    const relatedLink = makePreciseLink(related, relatedRef.subpath, draft.relatedPreview);
    const sourceRef = ensureBlockReference(sourceOriginal, sourceBlock);
    let sourceContent = sourceRef.content;
    sourceContent = addDirectRelation(sourceRef.content, sourceRef.subpath, relatedLink);
    const sourceLink = makePreciseLink(sourceFile, sourceRef.subpath, draft.excerpt);
    const entry = buildMarkdown(draft, sourceLink, relatedLink);
    sourceContent = insertAssociation(sourceContent, entry);
    await this.app.vault.modify(related, relatedContent);
    await this.app.vault.modify(sourceFile, sourceContent);
    new import_obsidian.Notice(`\u5DF2\u5EFA\u7ACB\u7CBE\u786E\u94FE\u63A5\u5E76\u5199\u5165 ${sourceFile.basename}`);
  }
};
