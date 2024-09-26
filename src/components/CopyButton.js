import React, { useState } from "react";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneIcon from "@mui/icons-material/Done";

import { Box } from "@mui/material";

/**
 * This component receives a text and shows an icon of copy. If the user clicks
 * the icon, this component copies the text to the clipboard while an
 * animation is plays.
 */
function CopyButton({ text }) {
  const [isJustCopied, setIsJustCopied] = useState(false);

  const copy = () => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setIsJustCopied(true);
        setTimeout(() => {
          setIsJustCopied(false);
        }, 2000);
      })
      .catch((err) => {
        console.error("Error - copy to clipboard: ", err);
      });
  };

  return (
    <>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          padding: 0.5,
          borderRadius: 1.5,
          "&:hover": {
            backgroundColor: "#eee",
            cursor: "pointer",
          },
        }}
        onClick={copy}
      >
        {isJustCopied ? (
          <DoneIcon sx={{ fontSize: "1rem" }} titleAccess="Copied" />
        ) : (
          <ContentCopyIcon sx={{ fontSize: "1rem" }} titleAccess="Copy" />
        )}
      </Box>
    </>
  );
}

export default CopyButton;
