pragma solidity ^0.4.11;

contract Owned {

    address owner;

    function Owned() {
        owner = msg.sender;
    }

    function kill() {
        if (msg.sender == owner) selfdestruct(owner);
    }
}

contract Device {

    struct Id {
        string manufacturer;
        string model;
        string serialNumber;
    }

    Id public deviceId;

    function Device(string _manufacturer, string _model, string _serialNumber) public {
        deviceId = Id({
            manufacturer : _manufacturer,
            model : _model,
            serialNumber : _serialNumber
            });
    }
}

contract DataLogger is Device, Owned {

    struct LogEntry {
        uint timestamp;
        uint value;
    }

    LogEntry[] public registry;

    function DataLogger(string _manufacturer, string _model, string _serialNumber) Device(_manufacturer, _model, _serialNumber) public {}

    function log(uint _timestamp, uint _value){
        registry.push(
            LogEntry({
            timestamp : _timestamp,
            value : _value
            }));
    }

    function getLogSize() returns (uint size){
        return registry.length;
    }

}