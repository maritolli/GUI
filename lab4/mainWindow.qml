import QtQuick 2.12
import QtQuick.Window 2.12

import "."

Window {
    id: root
    visible: true
    width: 1000
    height: 800
    minimumWidth: 640
    minimumHeight: 480
    title: "Лабораторная работа №4 — Painter"

    Rectangle {
        id: tools
        width: parent.width
        height: 180
        color: "#545454"

        property color paintColor: "#33B5E5"
        property int thickness: 1
        property int spacing: 4

        Row {
            spacing: 18
            anchors.centerIn: parent

            Column {
                spacing: tools.spacing

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "white"
                    font.pixelSize: 16
                    text: "Выбор цвета"
                }

                Row {
                    spacing: tools.spacing

                    Repeater {
                        model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]

                        Square {
                            active: tools.paintColor === color
                            color: modelData
                            onClicked: tools.paintColor = color
                        }
                    }
                }
            }

            Column {
                spacing: tools.spacing

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "white"
                    font.pixelSize: 16
                    text: "Толщина маркера"
                }

                Row {
                    spacing: tools.spacing

                    Repeater {
                        model: [1, 2, 3, 4, 5]

                        Circle {
                            active: tools.thickness === thickness
                            thickness: modelData
                            text: thickness
                            onClicked: tools.thickness = thickness
                        }
                    }
                }
            }

            Rectangle {
                id: saveButton
                width: 130
                height: 42
                anchors.verticalCenter: parent.verticalCenter
                radius: 5
                color: saveMouseArea.pressed ? "#d0d0d0" : "white"
                border.color: "#222222"

                Text {
                    anchors.centerIn: parent
                    color: "#222222"
                    font.pixelSize: 16
                    text: "Сохранить"
                }

                MouseArea {
                    id: saveMouseArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: _backend.saveNow()
                }
            }
        }
    }

    Rectangle {
        id: statusBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 34
        color: "#eeeeee"
        border.color: "#cccccc"

        Text {
            id: statusText
            anchors.fill: parent
            anchors.leftMargin: 12
            verticalAlignment: Text.AlignVCenter
            color: "#333333"
            text: "Автосохранение включено (каждые 5 секунд)"
        }
    }

    Item {
        id: canvasViewport
        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: statusBar.top
            margins: 8
        }
        clip: true

        Rectangle {
            id: canvasBackground
            anchors.fill: canvas
            color: "white"
            border.color: "#cccccc"
            scale: canvas.scale
        }

        Canvas {
            id: canvas
            anchors.centerIn: parent

            // Размер внутреннего буфера не меняется вместе с окном. Меняется
            // только визуальный масштаб, поэтому нарисованное не пропадает.
            width: 984
            height: 600
            scale: Math.min(canvasViewport.width / width,
                            canvasViewport.height / height)

            property real lastX
            property real lastY
            property color paintColor: tools.paintColor

            onPaint: {
                var context = getContext("2d")
                context.lineWidth = tools.thickness
                context.lineCap = "round"
                context.lineJoin = "round"
                context.strokeStyle = canvas.paintColor
                context.beginPath()
                context.moveTo(lastX, lastY)

                lastX = paintArea.mouseX
                lastY = paintArea.mouseY

                context.lineTo(lastX, lastY)
                context.stroke()
            }

            MouseArea {
                id: paintArea
                anchors.fill: parent
                cursorShape: Qt.CrossCursor

                onPressed: {
                    canvas.lastX = mouseX
                    canvas.lastY = mouseY
                }

                onPositionChanged: {
                    canvas.requestPaint()
                    _backend.markDirty()
                }
            }
        }
    }

    Connections {
        target: _backend

        onSaveRequested: {
            _backend.saveCanvas(canvas.toDataURL("image/png"))
        }

        onStatusChanged: {
            statusText.text = arguments[0]
        }
    }
}
