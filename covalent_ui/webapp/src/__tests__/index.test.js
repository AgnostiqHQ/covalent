import React from 'react'
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import ReactDOM from 'react-dom'
import App from "../App";

jest.mock("react-dom", () => ({ render: jest.fn() }));

describe("testing index",()=>{
    test("mock store",()=>{
        const mockStore = configureMockStore([thunk]);
        expect(mockStore).toBeDefined();
    })
    test("rendering react dom",()=>{
        const div = document.createElement("div");
        div.id = "root";
        document.body.appendChild(div);
        require("../index");
        expect(ReactDOM.render).toHaveBeenCalled();
    })
})
