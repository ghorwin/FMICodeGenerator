#!/usr/bin/env python3

# Custom tooltip popup (rounded card with soft shadow and palette-aware colors).
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
#
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# See FMIGenerator.py for the full license text.

import math
import re

from PyQt6 import sip
from PyQt6.QtCore import QObject, QPoint, QRectF, QTimer, QElapsedTimer, QEvent, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen, QTextDocument, QGuiApplication
from PyQt6.QtWidgets import QApplication, QAbstractButton, QFrame, QLabel, QVBoxLayout, QWidget


class TooltipPopup(QWidget):
	"""Custom tooltip popup: opaque raised card with a soft drop shadow and palette-aware colors.

	Rich text of the form "<b>Title</b><br><br>Body<br><br><i>Note</i>" is split into a bold title,
	the body and a muted note below a hairline; any other text is shown as body only.
	"""

	SHADOW_MARGIN = 8		# shadow margin around the content area in pixels
	CORNER_RADIUS = 6		# corner radius of the popup background
	MAX_TEXT_WIDTH = 340	# maximum width of the text column in pixels

	TITLE_RX = re.compile(r"^<b>(.*?)</b>(?:\s*<br\s*/?>)+", re.DOTALL | re.IGNORECASE)
	NOTE_RX = re.compile(r"(?:<br\s*/?>\s*)+<i>((?:(?!<i>).)*)</i>$", re.DOTALL | re.IGNORECASE)

	def __init__(self, parent=None):
		super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

		self.m_bgColor = QColor()
		self.m_borderColor = QColor()
		self.m_dark = False

		self.m_title = self.createLabel()
		f = self.m_title.font()
		f.setBold(True)
		self.m_title.setFont(f)
		self.m_body = self.createLabel()
		self.m_separator = QFrame(self)
		self.m_separator.setFixedHeight(1)
		self.m_note = self.createLabel()

		lay = QVBoxLayout(self)
		# content margins = padding inside card + shadow margin outside
		m = TooltipPopup.SHADOW_MARGIN
		lay.setContentsMargins(m + 12, m + 10, m + 12, m + 10)
		lay.setSpacing(6)
		lay.addWidget(self.m_title)
		lay.addWidget(self.m_body)
		lay.addWidget(self.m_separator)
		lay.addWidget(self.m_note)


	def setContent(self, html):
		body = html.strip()
		title = ""
		note = ""
		m = TooltipPopup.TITLE_RX.match(body)
		if m:
			title = m.group(1)
			body = body[m.end():]
		m = TooltipPopup.NOTE_RX.search(body)
		if m:
			note = m.group(1)
			body = body[:m.start()]
		self.m_title.setText(title)
		self.m_title.setVisible(len(title) != 0)
		self.m_body.setText(body)
		self.m_body.setVisible(len(body) != 0)
		self.m_note.setText(note)
		self.m_note.setVisible(len(note) != 0)
		self.m_separator.setVisible(len(note) != 0 and (len(body) != 0 or len(title) != 0))

		# QLabel's word-wrap heuristic wraps far below the maximum width, so fix the text column
		# width to the widest unwrapped text, limited to MAX_TEXT_WIDTH.
		w = 0
		for l in (self.m_title, self.m_body, self.m_note):
			if len(l.text()) == 0:
				continue
			doc = QTextDocument()
			doc.setDocumentMargin(0)
			doc.setDefaultFont(l.font())
			doc.setHtml(l.text())
			w = max(w, int(math.ceil(doc.idealWidth())))
		w = min(w, TooltipPopup.MAX_TEXT_WIDTH)
		for l in (self.m_title, self.m_body, self.m_note):
			l.setFixedWidth(w)


	@staticmethod
	def shadowMargin():
		"""Width of the transparent shadow margin around the card in pixels."""
		return TooltipPopup.SHADOW_MARGIN


	@staticmethod
	def backgroundColor(pal):
		"""Card background color for the given palette."""
		window = pal.color(QPalette.ColorRole.Window)
		if window.lightness() < 128:
			return window.lighter(118)
		return pal.color(QPalette.ColorRole.Base)


	def updateStyle(self):
		pal = QApplication.palette()
		window = pal.color(QPalette.ColorRole.Window)
		fg = pal.color(QPalette.ColorRole.WindowText)
		self.m_dark = window.lightness() < 128
		self.m_bgColor = TooltipPopup.backgroundColor(pal)
		self.m_borderColor = window.lighter(170) if self.m_dark else window.darker(115)
		sepColor = window.lighter(150) if self.m_dark else window.darker(106)
		# note text: 35 % of the way from text to background color
		bg = self.m_bgColor
		noteColor = QColor.fromRgbF(
			fg.redF() + 0.35*(bg.redF() - fg.redF()),
			fg.greenF() + 0.35*(bg.greenF() - fg.greenF()),
			fg.blueF() + 0.35*(bg.blueF() - fg.blueF()))

		labelStyle = "QLabel {{ color: {}; background: transparent; }}"
		self.m_title.setStyleSheet(labelStyle.format(fg.name()))
		self.m_body.setStyleSheet(labelStyle.format(fg.name()))
		self.m_note.setStyleSheet(labelStyle.format(noteColor.name()))
		self.m_separator.setStyleSheet("QFrame {{ background: {}; border: none; }}".format(sepColor.name()))
		self.update()


	def paintEvent(self, event):
		p = QPainter(self)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)

		m = TooltipPopup.SHADOW_MARGIN
		r = TooltipPopup.CORNER_RADIUS
		# card rect (inset by shadow margin)
		card = QRectF(self.rect()).adjusted(m, m, -m, -m)

		# soft shadow, shifted slightly downward: translucent rounded rects fading outward
		p.setPen(Qt.PenStyle.NoPen)
		maxAlpha = 22 if self.m_dark else 10
		for i in range(m, 0, -1):
			f = 1.0 - (i - 1)/m
			p.setBrush(QColor(0, 0, 0, int(maxAlpha*f*f)))
			shadowRect = card.adjusted(-i, -i + 2, i, i + 2)
			p.drawRoundedRect(shadowRect, r + i, r + i)

		path = QPainterPath()
		path.addRoundedRect(card.adjusted(0.5, 0.5, -0.5, -0.5), r, r)
		p.setBrush(self.m_bgColor)
		p.setPen(QPen(self.m_borderColor, 1.0))
		p.drawPath(path)
		p.end()


	def createLabel(self):
		l = QLabel(self)
		l.setTextFormat(Qt.TextFormat.RichText)
		l.setWordWrap(True)
		return l



# Popups hidden less than this many milliseconds ago let the next popup show without delay.
QUICK_SWITCH_MS = 400

# Measures the time since any popup was last hidden.
_sinceLastHide = QElapsedTimer()


class TooltipPopupController(QObject):
	"""Owns the popup widget and the show-delay timer and handles the popup lifecycle."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.m_content = ""
		self.m_globalPos = QPoint()
		self.m_anchor = None
		self.m_popup = None
		self.m_showTimer = None
		self.destroyed.connect(self._deletePopup)


	def _deletePopup(self):
		# popup is a top-level window without Qt parent, so it must be deleted manually
		if self.m_popup is not None:
			self.m_popup.deleteLater()
			self.m_popup = None


	def popupVisible(self):
		"""True if the popup exists and is shown (the popup may already be deleted during application shutdown)."""
		if self.m_popup is not None and sip.isdeleted(self.m_popup):
			self.m_popup = None
		return self.m_popup is not None and self.m_popup.isVisible()


	def setContent(self, richText):
		"""Sets the rich-text content shown by the popup. Empty disables the popup."""
		self.m_content = richText
		if self.popupVisible():
			self.m_popup.setContent(self.m_content)


	def content(self):
		return self.m_content


	def isEmpty(self):
		return len(self.m_content) == 0


	def scheduleShow(self, anchor, globalPos, delayMs=350):
		"""Schedules showing the popup below the left edge of anchor after delayMs milliseconds
		(globalPos is used when anchor is None). If another popup was hidden just before, it is
		shown without delay. If the popup is already visible, its content is refreshed.
		"""
		if len(self.m_content) == 0:
			return
		self.m_anchor = anchor
		self.m_globalPos = QPoint(globalPos)

		if not self.popupVisible() and self.m_popup is None:
			self.m_popup = TooltipPopup()
		if self.m_showTimer is None:
			self.m_showTimer = QTimer(self)
			self.m_showTimer.setSingleShot(True)
			self.m_showTimer.timeout.connect(self.showNow)

		# if already visible, just refresh content - don't restart the delay
		if self.m_popup.isVisible():
			self.m_popup.setContent(self.m_content)
			return

		if _sinceLastHide.isValid() and _sinceLastHide.elapsed() < QUICK_SWITCH_MS:
			delayMs = 0
		self.m_showTimer.stop()
		self.m_showTimer.setInterval(delayMs)
		self.m_showTimer.start()


	def hide(self):
		"""Hides the popup and cancels any pending show."""
		if self.m_showTimer is not None:
			self.m_showTimer.stop()
		if self.popupVisible():
			self.m_popup.hide()
			_sinceLastHide.start()


	def showNow(self):
		self.popupVisible() # resets m_popup if deleted
		if self.m_popup is None or len(self.m_content) == 0:
			return
		if self.m_anchor is not None and sip.isdeleted(self.m_anchor):
			self.m_anchor = None

		self.m_popup.setContent(self.m_content)
		self.m_popup.updateStyle()
		self.m_popup.adjustSize()

		m = TooltipPopup.shadowMargin()
		# position below the left edge of the anchor widget
		pos = self.m_globalPos + QPoint(0, 20)
		if self.m_anchor is not None:
			# align the card, not its shadow margin, with the anchor
			pos = self.m_anchor.mapToGlobal(QPoint(-m, self.m_anchor.height() + 4 - m))

		# keep popup on screen
		screen = QGuiApplication.screenAt(pos)
		if screen is not None:
			screenRect = screen.availableGeometry()
			if pos.x() + self.m_popup.width() > screenRect.right():
				pos.setX(screenRect.right() - self.m_popup.width())
			if pos.y() + self.m_popup.height() > screenRect.bottom():
				if self.m_anchor is not None:
					pos = self.m_anchor.mapToGlobal(QPoint(-m, -self.m_popup.height() - 4 + m))
				else:
					pos.setY(self.m_globalPos.y() - self.m_popup.height() - 4 + m)

		self.m_popup.move(pos)
		self.m_popup.show()



class TooltipEventFilter(QObject):
	"""Application-wide event filter that shows ordinary widget tooltips (QWidget.toolTip())
	in the TooltipPopup card instead of the native QToolTip.

	Install once after the QApplication has been created:

		app.installEventFilter(TooltipEventFilter(app))
	"""

	# buttons up to this height get the popup below their left edge, all other widgets at the cursor
	MAX_ANCHOR_HEIGHT = 60
	# a popup shown at the cursor is hidden once the mouse moved further than this (manhattan length)
	MAX_CURSOR_MOVE = 12

	def __init__(self, parent=None):
		super().__init__(parent)
		self.m_ctrl = TooltipPopupController(self)
		self.m_widget = None		# widget whose tooltip is currently shown/scheduled
		self.m_active = False		# true while a popup is shown or scheduled
		self.m_atCursor = False		# true if the popup is positioned at the cursor
		self.m_globalPos = QPoint()	# global cursor position when the popup was requested


	def eventFilter(self, watched, event):
		t = event.type()
		if t == QEvent.Type.ToolTip:
			# widgets without own tooltip either let the event propagate to their parent or show
			# their own (item) tooltips via QToolTip - leave both to Qt
			if not isinstance(watched, QWidget) or len(watched.toolTip()) == 0:
				return False
			# popup already shown for this widget: Qt re-sends tooltip events when the mouse rests again
			if watched is self.m_widget and not self.m_atCursor:
				return True
			self.m_ctrl.hide()
			self.m_active = True
			self.setWidget(watched)
			self.m_globalPos = event.globalPos()
			self.m_atCursor = not isinstance(watched, QAbstractButton) or watched.height() > TooltipEventFilter.MAX_ANCHOR_HEIGHT
			self.m_ctrl.setContent(TooltipEventFilter.toRichText(watched.toolTip()))
			# QEvent.ToolTip already arrives after Qt's tooltip delay, so show without further delay
			self.m_ctrl.scheduleShow(None if self.m_atCursor else watched, self.m_globalPos, 0)
			return True

		elif t == QEvent.Type.ToolTipChange:
			if self.widgetAlive() and watched is self.m_widget:
				if len(self.m_widget.toolTip()) == 0:
					self.hideTip()
				else:
					self.m_ctrl.setContent(TooltipEventFilter.toRichText(self.m_widget.toolTip()))

		elif t == QEvent.Type.MouseMove:
			if self.m_active and self.m_atCursor and \
				(event.globalPosition().toPoint() - self.m_globalPos).manhattanLength() > TooltipEventFilter.MAX_CURSOR_MOVE:
				self.hideTip()

		elif t in (QEvent.Type.Leave, QEvent.Type.Hide, QEvent.Type.EnabledChange):
			if self.widgetAlive() and watched is self.m_widget:
				self.hideTip()

		elif t in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick, QEvent.Type.Wheel,
				   QEvent.Type.KeyPress, QEvent.Type.WindowDeactivate, QEvent.Type.ApplicationDeactivate):
			if self.m_active:
				self.hideTip()

		return False


	def setWidget(self, w):
		# forget the widget when it is deleted
		if self.widgetAlive():
			try:
				self.m_widget.destroyed.disconnect(self.onWidgetDestroyed)
			except (TypeError, RuntimeError):
				pass
		self.m_widget = w
		if w is not None:
			w.destroyed.connect(self.onWidgetDestroyed)


	def widgetAlive(self):
		if self.m_widget is not None and sip.isdeleted(self.m_widget):
			self.m_widget = None
		return self.m_widget is not None


	def onWidgetDestroyed(self):
		self.m_widget = None
		if self.m_active:
			self.hideTip()


	def hideTip(self):
		"""Hides the popup and forgets the widget."""
		self.m_ctrl.hide()
		self.m_active = False
		self.setWidget(None)


	@staticmethod
	def toRichText(toolTip):
		"""Converts plain-text tooltips to rich text (escaped, line breaks kept); rich text is returned unchanged."""
		if Qt.mightBeRichText(toolTip):
			return toolTip
		return toolTip.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
