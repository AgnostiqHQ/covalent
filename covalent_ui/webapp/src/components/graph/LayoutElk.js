/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import _ from 'lodash'
import ELK from 'elkjs/lib/elk.bundled.js'
import { isNode } from 'react-flow-renderer'
import { isParameter, isPostProcess, Prettify } from '../../utils/misc'

const nodeLabel = (type, name) => {
  switch (type) {
    case 'parameter':
      return name?.replace(':parameter:', '')
    case 'electron_list':
      return name?.replace(':electron_list:', 'electron list')
    case 'sublattice':
      return name?.replace(':sublattice:', 'Sublattice:')
    default:
      return name
  }
}

/**
 * Filter graph by node type.
 */
const filterGraph = (graph, nodePredicate) => {
  const nodes = graph?.nodes?.filter(nodePredicate)
  const nodeSet = new Set(nodes?.map((i) => i.id))
  const links = graph?.links?.filter(
    ({ source, target }) => nodeSet.has(source) && nodeSet.has(target)
  )
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
  preview,
  showPostProcess,
  prettify
) => {
  if (!showPostProcess) {
    graph = filterGraph(graph, (node) => !isPostProcess(node))
  }
  if (!showParams) {
    graph = filterGraph(graph, (node) => !isParameter(node))
  }

  const nodes = _.map(graph.nodes, (node) => {
    const handlePositions = getHandlePositions(direction)
    const isParam = isParameter(node)
    const name = isParam
      ? node?.name?.replace(':parameter:', '')
      : prettify
        ? Prettify(node.name, node.type)
        : nodeLabel(node?.type, node.name)
    return {
      id: String(node.id),
      type: isParam ? 'parameter' : 'electron',
      data: {
        fullName: name || 'parameter',
        label: hideLabels
          ? _.truncate(name || 'parameter', { length: 0 })
          : _.truncate(name || 'parameter', { length: 70 }),
        status: node.status,
        executor: preview ? node?.metadata.executor_name : node.executor_label,
        node_id: preview ? node.id : node.node_id,
        hideLabels: hideLabels,
        nodeType: node.type,
        preview,
        sublattices_id: node.sublattice_dispatch_id
          ? node.sublattice_dispatch_id
          : null,
        isQelectron: node?.qelectron_data_exists
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
  preview,
  showPostProcess,
  prettify
) => {
  const elements = mapGraphToElements(
    graph,
    direction,
    showParams,
    hideLabels,
    preview,
    showPostProcess,
    prettify
  )
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
