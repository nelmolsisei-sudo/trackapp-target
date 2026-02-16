// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Token.sol";

contract TokenTest is Test {
    Token token;
    address deployer;
    address alice = address(0x1);
    address bob = address(0x2);

    function setUp() public {
        deployer = address(this);
        token = new Token("Test Token", "TT");
    }

    // ======================== Metadata ========================

    function test_name_and_symbol() public view {
        assertEq(token.name(), "Test Token");
        assertEq(token.symbol(), "TT");
        assertEq(token.decimals(), 18);
        assertEq(token.owner(), deployer);
    }

    // ======================== Minting ========================

    function test_owner_can_mint() public {
        token.mint(alice, 1000 ether);
        assertEq(token.balanceOf(alice), 1000 ether);
        assertEq(token.totalSupply(), 1000 ether);
    }

    function test_non_owner_cannot_mint() public {
        vm.prank(alice);
        vm.expectRevert();
        token.mint(alice, 1000 ether);
    }

    function test_cannot_mint_to_zero_address() public {
        vm.expectRevert();
        token.mint(address(0), 1000 ether);
    }

    // ======================== Transfer ========================

    function test_transfer() public {
        token.mint(deployer, 1000 ether);
        token.transfer(alice, 400 ether);
        assertEq(token.balanceOf(deployer), 600 ether);
        assertEq(token.balanceOf(alice), 400 ether);
    }

    function test_transfer_insufficient_balance() public {
        token.mint(deployer, 100 ether);
        vm.expectRevert();
        token.transfer(alice, 200 ether);
    }

    function test_cannot_transfer_to_zero_address() public {
        token.mint(deployer, 1000 ether);
        vm.expectRevert();
        token.transfer(address(0), 100 ether);
    }

    // ======================== Approve + TransferFrom ========================

    function test_approve_and_transferFrom() public {
        token.mint(deployer, 1000 ether);
        token.approve(alice, 500 ether);
        assertEq(token.allowance(deployer, alice), 500 ether);

        vm.prank(alice);
        token.transferFrom(deployer, bob, 300 ether);

        assertEq(token.balanceOf(deployer), 700 ether);
        assertEq(token.balanceOf(bob), 300 ether);
        assertEq(token.allowance(deployer, alice), 200 ether);
    }

    function test_transferFrom_insufficient_allowance() public {
        token.mint(deployer, 1000 ether);
        token.approve(alice, 100 ether);

        vm.prank(alice);
        vm.expectRevert();
        token.transferFrom(deployer, bob, 200 ether);
    }

    function test_transferFrom_insufficient_balance() public {
        token.mint(deployer, 100 ether);
        token.approve(alice, 500 ether);

        vm.prank(alice);
        vm.expectRevert();
        token.transferFrom(deployer, bob, 200 ether);
    }

    function test_cannot_transferFrom_to_zero_address() public {
        token.mint(deployer, 1000 ether);
        token.approve(alice, 500 ether);

        vm.prank(alice);
        vm.expectRevert();
        token.transferFrom(deployer, address(0), 100 ether);
    }
}
