import * as React from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

export function LayoutOptions(props) {
	// const { anchorEl, handleClick, handleClose, handleArchive, handleDelete, handleEdit, handleMove, handleRestart, open } = props;
	const {
		algorithm,
		handleChangeAlgorithm,
		open,
		anchorEl,
		handleClose
	} = props;
	// const options=['box','mrtree','rectpacking','stress','disco']
	const options = [{
		optionName: 'Layered',
		optionValue: 'layered'
	},
	{
		optionName: 'Tree',
		optionValue: 'mrtree'
	},
	{
		optionName: 'Force',
		optionValue: 'force'
	},
	{
		optionName: 'Rectangular',
		optionValue: 'rectpacking'
	},
	{
		optionName: 'Box',
		optionValue: 'box'
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
					transform: 'translateX(-5px) translateY(5px)'
				}
			}}
		>
			{options.map((option) => (
				<MenuItem
				sx={{
					fontSize:'0.875rem',
					'&.Mui-selected': {
                        backgroundColor: '#1C1C46'
                    }
				}}
				selected={algorithm===option.optionValue} key={option.optionName} onClick={() => handleChangeAlgorithm(option.optionValue)}>
					{option.optionName}
				</MenuItem>
			))}
		</Menu>
	);
}
