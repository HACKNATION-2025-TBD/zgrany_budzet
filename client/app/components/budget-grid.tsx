"use client";

import React, { useState } from "react";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";

ModuleRegistry.registerModules([AllCommunityModule]);

const BudgetGrid = () => {
  // Row Data: The data to be displayed.
  const [rowData, setRowData] = useState([
    {
      kod: "010",
      nazwa: "Rolnictwo i łowiectwo",
      planowane: 1500000,
      wykonane: 1200000,
      jezyk: "English",
    },
    {
      kod: "020",
      nazwa: "Leśnictwo",
      planowane: 800000,
      wykonane: 650000,
      jezyk: "English",
    },
    {
      kod: "801",
      nazwa: "Oświata i wychowanie",
      planowane: 5000000,
      wykonane: 3750000,
      jezyk: "English", 
    },
    {
      kod: "851",
      nazwa: "Ochrona zdrowia",
      planowane: 3500000,
      wykonane: 2800000,
      jezyk: "English",
    },
    {
      kod: "900",
      nazwa: "Gospodarka komunalna",
      planowane: 2200000,
      wykonane: 1540000,
      jezyk: "English",
    },
    {
      kod: "754",
      nazwa: "Bezpieczeństwo publiczne",
      planowane: 950000,
      wykonane: 760000,
      jezyk: "English",
    },
  ]);

  // Column Definitions: Defines & controls grid columns.
  const [colDefs, setColDefs] = useState([
    {
      field: "kod" as const,
      editable: true,
      valueParser: (params: any) => {
        const newValue = params.newValue;
        if (Number.isNaN(Number(newValue))) {
          return params.oldValue;
        }
        return newValue;
      },
    },
    { field: "nazwa" as const, editable: true },
    { field: "planowane" as const, editable: true },
    { field: "wykonane" as const, editable: true },
    {
      field: "jezyk" as const,
      editable: true,
      cellEditor: "agSelectCellEditor",
      cellEditorParams: {
        values: ["English", "Spanish", "French", "Portuguese", "(other)"],
      },
    },
  ]);

  const defaultColDef = {
    flex: 1,
  };

  return (
    <AgGridReact
      rowData={rowData}
      columnDefs={colDefs}
      editType="singleCell"
      stopEditingWhenCellsLoseFocus={true}

      onCellEditingStopped={(event) => {
        console.log("Cell editing stopped:", event);
      }}
      onCellEditingStarted={(event) => {
        console.log("Cell editing started:", event);
      }}
      onCellValueChanged={(event) => {
        console.log("Cell value changed:", event);
    }}
      defaultColDef={defaultColDef}
    />
  );
};

export default BudgetGrid;
