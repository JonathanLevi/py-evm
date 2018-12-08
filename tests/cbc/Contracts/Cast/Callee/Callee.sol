pragma solidity ^0.4.20;

contract Callee {
    uint Y = 0;

    function setYto3() public payable {
        Y = 3;
    }

    function setYto7() public payable {
        Y = 7;
    }

}
