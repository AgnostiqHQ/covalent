import * as React from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

export function LayoutOptions(props) {
	// const { anchorEl, handleClick, handleClose, handleArchive, handleDelete, handleEdit, handleMove, handleRestart, open } = props;
	const {
		handleChangeAlgorithm,
		open,
		anchorEl,
		handleClose
	} = props;
	// const options=['box','mrtree','rectpacking','stress','disco']
	const options = [{
		optionName: 'Box',
		optionValue: 'box'
	},
	{
		optionName: 'Rectangular',
		optionValue: 'rectpacking'
	},
	{
		optionName: 'Tree',
		optionValue: 'mrtree'
	},
	{
		optionName: 'Stress',
		optionValue: 'stress'
	},
	{
		optionName: 'Force',
		optionValue: 'force'
	},
	{
		optionName: 'Layered',
		optionValue: 'layered'
	},
	{
		optionName: 'Old Layout',
		optionValue: 'oldLayout'
	}]
	return (
		<Menu
			variant="menu"
			anchorEl={anchorEl}
			open={open}
			onClose={handleClose}
			keepMounted={false}
			getContentAnchorEl={null}
			anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
			transformOrigin={{ vertical: 'top', horizontal: 'left' }}
			PaperProps={{
				style: {
					maxHeight: '300px',
					width: '170px',
					transform: 'translateX(-5px) translateY(5px)'
				}
			}}
		>
			{options.map((option) => (
				<MenuItem key={option.optionName} onClick={() => handleChangeAlgorithm(option.optionValue)}>
					{option.optionName}
				</MenuItem>
			))}
		</Menu>
	);
}
