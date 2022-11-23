/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */

import _ from 'lodash'
import ELK from 'elkjs/lib/elk.bundled.js'
import { isNode } from 'react-flow-renderer'
import { isParameter } from '../../utils/misc'

const nodeLabel = (type, name) => {
  switch (type) {
    case 'parameter':
      return name.replace(':parameter:', '')
    case 'electron_list':
      return name.replace(':electron_list:', 'electron list')
    case 'sublattice':
      return name.replace(':sublattice:', 'Sublattice:')
    default:
      return name
  }
}

/**
 * Filter graph by node type.
 */
const filterGraph = (graph, nodePredicate) => {
  const nodes = _.filter(graph.nodes, nodePredicate)
  const nodeSet = new Set(_.map(nodes, 'id'))
  const links = _.filter(graph.links, ({ source }) => nodeSet.has(source))
  return { nodes, links }
}

/**
 * Map Covalent graph nodes and links to ReactFlow graph elements.
 */
const mapGraphToElements = (
  graph,
  direction,
  showParams,
  hideLabels,
  preview
) => {
  if (!showParams) {
    graph = filterGraph(graph, (node) => !isParameter(node))
  }

  const nodes = _.map(graph.nodes, (node) => {
    const handlePositions = getHandlePositions(direction)
    const isParam = isParameter(node)
    const name = isParam
      ? _.trim(node.name, ':parameter:')
      : nodeLabel(node.type, node.name)
    return {
      id: String(node.id),
      type: isParam ? 'parameter' : 'electron',
      data: {
        fullName: name,
        label: hideLabels
          ? _.truncate(name, { length: 0 })
          : _.truncate(name, { length: 70 }),
        status: node.status,
        executor: preview ? node?.metadata.executor_name : node.executor_label,
        node_id: preview ? node.id : node.node_id,
        hideLabels: hideLabels,
        nodeType: node.type,
        preview,
        sublattices_id: node.sublattice_dispatch_id
          ? node.sublattice_dispatch_id
          : null,
      },
      targetPosition: handlePositions.target,
      sourcePosition: handlePositions.source,
    }
  })

  const edges = _.map(graph.links, (edge) => {
    const { source, target } = edge
    return {
      id: `${source}-${target}`,
      source: String(source),
      target: String(target),
      label: edge.edge_name,
      type: 'directed',
    }
  })

  return [...nodes, ...edges]
}

const assignNodePositions = async (
  graph,
  direction,
  showParams,
  algorithm,
  hideLabels,
  preview
) => {
  const elements = mapGraphToElements(graph, direction, showParams, hideLabels, preview)
  const nodes = []
  const edges = []
  const DEFAULT_HEIGHT = 75

  const elk = new ELK({
    defaultLayoutOptions: {
      'elk.algorithm': algorithm,
      'elk.direction': direction,
      'elk.edgeRouting': 'POLYLINE',
      'elk.layered.nodePlacement.strategy': 'SIMPLE',
      'elk.spacing.edgeEdge': hideLabels ? 10 : 20,
      'elk.spacing.nodeNode': hideLabels ? 60 : 40,
      'elk.spacing.edgeNode': hideLabels ? 60 : 40,
      'elk.spacing.edgeLabel': 10,
      'elk.layered.spacing.nodeNodeBetweenLayers': 80,
      'elk.layered.spacing.baseValue': hideLabels ? 40 : 10,
    },
  })
  _.each(elements, (el) => {
    if (isNode(el)) {
      nodes.push({
        id: el.id,
        width: _.size(el.data.label) * 15,
        height: DEFAULT_HEIGHT,
      })
    } else {
      edges.push({
        id: el.id,
        target: el.target,
        source: el.source,
      })
    }
  })

  const newGraph = await elk.layout({
    id: 'root',
    children: nodes,
    edges: edges,
  })
  return elements.map((el) => {
    if (isNode(el)) {
      const node = newGraph?.children?.find((n) => n.id === el.id)
      if (node?.x && node?.y && node?.width && node?.height) {
        el.position = {
          x: node.x,
          y: node.y,
        }
      }
    }
    return el
  })
}

/**
 * Returns source and target handle positions.
 *
 * @param {direction} 'LR'|'RL'|'TB'|'BT'
 *
 * @returns { source: <position>, target: <position> }
 */
const getHandlePositions = (direction) => {
  switch (direction) {
    case 'DOWN':
      return { source: 'bottom', target: 'top' }
    case 'UP':
      return { source: 'top', target: 'bottom' }
    case 'LEFT':
      return { source: 'left', target: 'right' }
    case 'RIGHT':
      return { source: 'right', target: 'left' }

    default:
      throw new Error(`Illegal direction: ${direction}`)
  }
}

export default assignNodePositions
