"""Central Qt stylesheet for the first FloatNotes UI foundation."""

APP_STYLE = """
QMainWindow {
    background: #EEF1F5;
}

QWidget#AppRoot {
    background: #EEF1F5;
}

QWidget {
    color: #1F2933;
    font-family: "Segoe UI", "Inter", "Arial";
    font-size: 14px;
}

QFrame#Sidebar {
    background: rgba(248, 250, 252, 0.94);
    border-right: 1px solid rgba(31, 41, 51, 0.08);
}

QFrame#ContentPanel {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(31, 41, 51, 0.08);
    border-radius: 18px;
}

QFrame#DialogPanel {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(31, 41, 51, 0.10);
    border-radius: 18px;
}

QFrame#PanelBody {
    background: transparent;
    border: none;
}

QLabel#AppTitle {
    font-size: 24px;
    font-weight: 700;
}

QLabel#SectionTitle {
    font-size: 22px;
    font-weight: 650;
}

QLabel#DialogTitle {
    color: #111827;
    font-size: 20px;
    font-weight: 700;
}

QLabel#DialogMessage {
    color: #6B7280;
    font-size: 14px;
    line-height: 1.35;
}

QLabel#MutedText {
    color: #6B7280;
}

QLabel#SidebarCaption {
    color: #8A94A3;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

QLabel#CountBadge {
    color: #1D4ED8;
    background: rgba(37, 99, 235, 0.10);
    border: 1px solid rgba(37, 99, 235, 0.16);
    border-radius: 13px;
    padding: 8px 14px;
    font-weight: 700;
}

QLabel#CountBadge[done="true"] {
    color: #0E8F55;
    background: rgba(16, 185, 129, 0.10);
    border: 1px solid rgba(16, 185, 129, 0.16);
}

QLabel#EmptyState {
    color: #7B8491;
    background: rgba(248, 250, 252, 0.96);
    border: 1px solid rgba(31, 41, 51, 0.06);
    border-radius: 16px;
    padding: 24px;
}

QLabel#SelectionHint {
    color: #A0A8B5;
    font-size: 14px;
    font-style: italic;
    padding: 24px;
}

QFrame#InputFooter {
    background: rgba(248, 250, 252, 0.78);
    border-top: 1px solid rgba(31, 41, 51, 0.08);
    border-bottom-left-radius: 18px;
    border-bottom-right-radius: 18px;
}

QFrame#InputBar {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(31, 41, 51, 0.12);
    border-radius: 16px;
}

QListWidget#ListNavigation,
QListWidget#NotesItems {
    background: transparent;
    border: none;
    outline: 0;
}

QListWidget#ListNavigation::item {
    background: transparent;
    border: none;
    padding: 0;
    margin: 4px 0;
}

QListWidget#ListNavigation::item:hover {
    background: transparent;
}

QListWidget#ListNavigation::item:selected {
    background: transparent;
}

QFrame#ListRow {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
}

QFrame#ListRow[active="true"] {
    background: rgba(37, 99, 235, 0.10);
    border: 1px solid rgba(37, 99, 235, 0.14);
}

QFrame#ListAccent {
    background: transparent;
    border-radius: 2px;
}

QFrame#ListAccent[active="true"] {
    background: #2563EB;
}

QLabel#ListIcon {
    color: #7B8491;
    background: rgba(255, 255, 255, 0.84);
    border: 1px solid rgba(31, 41, 51, 0.10);
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
}

QLabel#ListIcon[active="true"] {
    color: #2563EB;
    border: 1px solid rgba(37, 99, 235, 0.22);
}

QLabel#ListName {
    color: #566070;
    font-size: 14px;
    font-weight: 500;
}

QLabel#ListName[active="true"] {
    color: #111827;
    font-weight: 650;
}

QLabel#ListCountBadge {
    color: #5F6B7A;
    background: rgba(31, 41, 51, 0.06);
    border: 1px solid rgba(31, 41, 51, 0.06);
    border-radius: 10px;
    font-weight: 700;
}

QLabel#ListCountBadge[active="true"] {
    color: #1D4ED8;
    background: rgba(37, 99, 235, 0.10);
    border: 1px solid rgba(37, 99, 235, 0.14);
}

QListWidget#NotesItems::item {
    background: transparent;
    border: none;
    padding: 0;
    margin: 4px 0;
}

QListWidget#NotesItems::item:hover {
    background: transparent;
}

QListWidget#NotesItems::item:selected {
    background: transparent;
}

QFrame#TaskRow {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(31, 41, 51, 0.07);
    border-radius: 12px;
}

QFrame#TaskRow:hover {
    border: 1px solid rgba(31, 41, 51, 0.10);
    background: rgba(255, 255, 255, 1.0);
}

QFrame#TaskRow[active="true"] {
    border: 1px solid rgba(37, 99, 235, 0.42);
    background: rgba(248, 251, 255, 0.98);
}

QFrame#TaskActiveAccent {
    background: transparent;
    border-radius: 2px;
}

QFrame#TaskActiveAccent[active="true"] {
    background: rgba(37, 99, 235, 0.70);
}

QCheckBox#TaskCheck {
    spacing: 0;
}

QCheckBox#TaskCheck::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid rgba(31, 41, 51, 0.20);
    background: white;
}

QCheckBox#TaskCheck[active="true"]::indicator {
    border: 1px solid rgba(37, 99, 235, 0.28);
}

QCheckBox#TaskCheck::indicator:checked {
    background: #2563EB;
    border: 1px solid #2563EB;
}

QLabel#TaskText {
    color: #1F2933;
    font-size: 14px;
}

QLabel#TaskText[active="true"] {
    color: #111827;
    font-weight: 550;
}

QLabel#TaskText[completed="true"] {
    color: #8A94A3;
}

QFrame#TaskRowActions {
    background: transparent;
    border: none;
}

QPushButton#TaskRowButton,
QPushButton#TaskRowDangerButton {
    border-radius: 8px;
    min-height: 26px;
    min-width: 86px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#TaskRowButton {
    background: rgba(255, 255, 255, 0.56);
    border: 1px solid rgba(31, 41, 51, 0.09);
    color: #475467;
}

QPushButton#TaskRowButton:hover {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(37, 99, 235, 0.18);
    color: #344054;
}

QPushButton#TaskRowDangerButton {
    background: rgba(254, 242, 242, 0.46);
    border: 1px solid rgba(180, 35, 24, 0.11);
    color: #B42318;
}

QPushButton#TaskRowDangerButton:hover {
    background: rgba(254, 226, 226, 0.74);
    border: 1px solid rgba(180, 35, 24, 0.18);
    color: #912018;
}

QStatusBar {
    color: #6B7280;
    background: #EEF1F5;
}

QPushButton {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 15px;
    font-weight: 600;
}

QPushButton#AddItemButton {
    min-width: 112px;
    min-height: 36px;
    padding: 8px 14px;
}

QPushButton#DialogPrimaryButton,
QPushButton#DialogDangerButton {
    min-width: 104px;
    padding: 9px 15px;
}

QPushButton#DialogDangerButton {
    background: rgba(184, 55, 55, 0.12);
    color: #9B2C2C;
}

QPushButton#DialogDangerButton:hover {
    background: rgba(184, 55, 55, 0.20);
}

QPushButton:hover {
    background: #1D4ED8;
}

QPushButton:disabled {
    background: #D7DCE2;
    color: #7B8491;
}

QPushButton#SecondaryButton {
    background: rgba(31, 41, 51, 0.08);
    color: #1F2933;
}

QPushButton#SecondaryButton:hover {
    background: rgba(31, 41, 51, 0.14);
}

QPushButton#SecondaryButton:disabled {
    background: rgba(31, 41, 51, 0.05);
    color: #9AA3AF;
}

QPushButton#DangerButton {
    background: rgba(184, 55, 55, 0.10);
    color: #9B2C2C;
}

QPushButton#DangerButton:hover {
    background: rgba(184, 55, 55, 0.18);
}

QPushButton#DangerButton:disabled {
    background: rgba(31, 41, 51, 0.05);
    color: #9AA3AF;
}

QLineEdit {
    background: white;
    border: none;
    border-radius: 12px;
    padding: 8px 12px;
}

QLineEdit:focus {
    border: none;
}

QLineEdit#DialogInput {
    background: rgba(248, 250, 252, 0.96);
    border: 1px solid rgba(31, 41, 51, 0.12);
    border-radius: 12px;
    padding: 10px 12px;
    selection-background-color: rgba(37, 99, 235, 0.22);
}

QLineEdit#DialogInput:focus {
    border: 1px solid rgba(37, 99, 235, 0.35);
}

QMenu {
    background: white;
    border: 1px solid rgba(31, 41, 51, 0.10);
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 18px;
    border-radius: 8px;
}

QMenu::item:selected {
    background: rgba(37, 99, 235, 0.10);
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: rgba(31, 41, 51, 0.16);
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
"""
