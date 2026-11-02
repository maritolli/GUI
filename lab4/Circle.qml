import QtQuick 2.0

Rectangle {
    id: root

    property bool active: false
    property int thickness: 1
    property string text: ""

    signal clicked

    width: 25
    height: width
    radius: width / 2
    color: active ? "black" : "white"
    border.color: active ? "white" : "black"
    border.width: active ? 1 : 1.2

    Text {
        anchors.centerIn: parent
        color: root.active ? "white" : "black"
        text: root.text
    }

    MouseArea {
        anchors.fill: parent
        onClicked: root.clicked()
    }

    Behavior on color {
        ColorAnimation { duration: 150 }
    }
}
