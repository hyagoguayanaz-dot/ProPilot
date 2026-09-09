"""
CTkEditableLabel - Editable label widget for CustomTkinter.
A simple editable label implementation.
"""

import customtkinter as ctk


class CTkEditableLabel(ctk.CTkLabel):
    """Editable label widget for CustomTkinter."""
    
    def __init__(self, master, text="", editable=False, **kwargs):
        self._editable = editable
        self._original_text = text
        
        super().__init__(master, text=text, **kwargs)
        
        if editable:
            self._setup_editable()
    
    def _setup_editable(self):
        """Set up editable functionality."""
        self.bind("<Double-Button-1>", self._start_editing)
    
    def _start_editing(self, event=None):
        """Start editing mode."""
        self._editing_var = ctk.StringVar(value=self.cget("text"))
        
        self._entry = ctk.CTkEntry(
            self.master,
            textvariable=self._editing_var,
            width=self.winfo_width(),
            **self._entry_kwargs if hasattr(self, '_entry_kwargs') else {}
        )
        
        self._entry.bind("<Return>", self._stop_editing)
        self._entry.bind("<Escape>", self._cancel_editing)
        self._entry.focus_set()
        
        # Position entry over label
        self._entry.place(
            x=event.x if event else 0,
            y=event.y if event else 0,
            relwidth=1
        )
    
    def _stop_editing(self, event=None):
        """Stop editing and save changes."""
        new_text = self._editing_var.get()
        self.configure(text=new_text)
        self._original_text = new_text
        self._entry.destroy()
    
    def _cancel_editing(self, event=None):
        """Cancel editing and restore original text."""
        self.configure(text=self._original_text)
        self._editing_var = None
        self._entry.destroy()
    
    def set_editable(self, editable: bool):
        """Set whether the label is editable."""
        if editable and not self._editable:
            self._setup_editable()
        self._editable = editable