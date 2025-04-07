import React, { useState, useContext } from "react";
import {
  Filter,
  CheckCircle,
  Clock,
  AlertCircle,
  File,
  Calendar,
  Search,
  Trash2,
  Eye,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import EmptyState from "./EmptyState";
import { useDocuments, useDeleteDocument } from "@/hooks/useDocuments";
import { DocumentResponse } from "@/types/api";
import { SelectedDocsContext } from "@/contexts/SelectedDocsContext";
import { toast } from "sonner";

const DocumentList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);
  const { selectedDocIds, setSelectedDocIds } = useContext(SelectedDocsContext);

  const pageSize = 10;
  const {
    data: documentList,
    isLoading,
    isError,
  } = useDocuments(pageSize, (page - 1) * pageSize);
  const { mutate: deleteDocument, isPending: isDeleting } = useDeleteDocument();

  // Filter documents based on search term and filters
  const filteredDocuments =
    documentList?.documents.filter((doc) => {
      const matchesSearch = doc.file_name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesStatus =
        statusFilter === "all" || doc.embedding_status === statusFilter;
      const matchesType =
        typeFilter === "all" ||
        doc.file_type.toLowerCase() === typeFilter.toLowerCase();

      return matchesSearch && matchesStatus && matchesType;
    }) || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processed":
        return <CheckCircle className="h-4 w-4 text-docflow-success" />;
      case "pending":
        return <Clock className="h-4 w-4 text-docflow-warning" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-docflow-error" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  const getDocumentTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return "bg-red-100 text-red-800";
      case "docx":
        return "bg-blue-100 text-blue-800";
      case "xlsx":
        return "bg-green-100 text-green-800";
      case "csv":
        return "bg-purple-100 text-purple-800";
      case "txt":
        return "bg-gray-100 text-gray-800";
      case "md":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    else return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleDeleteDocument = (documentId: string) => {
    deleteDocument(documentId);
    setSelectedDoc(null);
  };

  const handleToggleDocumentSelection = (doc: DocumentResponse) => {
    // Only processed documents can be selected for querying
    if (doc.embedding_status !== "processed") {
      toast.error("Only processed documents can be selected for querying");
      return;
    }

    // Toggle document selection
    if (selectedDocIds.includes(doc.document_id)) {
      setSelectedDocIds(selectedDocIds.filter((id) => id !== doc.document_id));
      toast.info(`Document "${doc.file_name}" removed from query selection`);
    } else {
      setSelectedDocIds([...selectedDocIds, doc.document_id]);
      toast.success(`Document "${doc.file_name}" added to query selection`);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-3">
            {Array(5)
              .fill(0)
              .map((_, idx) => (
                <div key={idx} className="h-12 bg-gray-100 rounded"></div>
              ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <EmptyState
          icon={<AlertCircle className="h-10 w-10 text-docflow-error" />}
          title="Failed to load documents"
          description="An error occurred while trying to fetch your documents. Please try again."
          buttonText="Retry"
          buttonAction={() => window.location.reload()}
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex flex-col gap-4 mb-6">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Document List</h2>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search documents..."
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="processed">Processed</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>

          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="pdf">PDF</SelectItem>
              <SelectItem value="txt">TXT</SelectItem>
              <SelectItem value="csv">CSV</SelectItem>
              <SelectItem value="md">MD</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {filteredDocuments.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-docflow-secondary">
                    Name
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-docflow-secondary">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr
                    key={doc.document_id}
                    className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                      selectedDocIds.includes(doc.document_id)
                        ? "bg-blue-50 hover:bg-blue-100"
                        : ""
                    } ${
                      doc.embedding_status !== "processed"
                        ? "opacity-60 cursor-not-allowed"
                        : ""
                    }`}
                    onClick={() => handleToggleDocumentSelection(doc)}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="flex-shrink-0">
                          {selectedDocIds.includes(doc.document_id) ? (
                            <CheckCircle className="h-5 w-5 text-docflow-success" />
                          ) : (
                            <File className="h-5 w-5 text-docflow-secondary" />
                          )}
                        </div>
                        <div className="flex-grow">
                          <span className="text-sm font-medium text-docflow-dark block">
                            {doc.file_name}
                          </span>
                          <div className="flex items-center mt-1">
                            <Badge
                              variant="secondary"
                              className={`text-xs mr-2 ${getDocumentTypeColor(
                                doc.file_type
                              )}`}
                            >
                              {doc.file_type.toUpperCase()}
                            </Badge>
                            <div className="flex items-center space-x-1 text-xs text-docflow-secondary">
                              {getStatusIcon(doc.embedding_status)}
                              <span className="capitalize">
                                {doc.embedding_status}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex items-center gap-1"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent row click
                            setSelectedDoc(doc);
                          }}
                        >
                          <Eye className="h-3.5 w-3.5" />
                          <span className="hidden sm:inline">View</span>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                    className={
                      page <= 1 ? "pointer-events-none opacity-50" : ""
                    }
                  />
                </PaginationItem>
                <PaginationItem>
                  <span className="text-sm">
                    Page {page} of{" "}
                    {Math.ceil((documentList?.total || 0) / pageSize)}
                  </span>
                </PaginationItem>
                <PaginationItem>
                  <PaginationNext
                    onClick={() => setPage((prev) => prev + 1)}
                    className={
                      page >= Math.ceil((documentList?.total || 0) / pageSize)
                        ? "pointer-events-none opacity-50"
                        : ""
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        </>
      ) : (
        <EmptyState
          icon={<Filter className="h-10 w-10 text-docflow-secondary" />}
          title="No documents found"
          description="Try adjusting your search or filter to find what you're looking for."
        />
      )}

      {/* Document details dialog */}
      {selectedDoc && (
        <Dialog
          open={!!selectedDoc}
          onOpenChange={(open) => !open && setSelectedDoc(null)}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Document Details</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              {/* Document ID and File Name in full width */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    Document ID
                  </h4>
                  <p className="text-sm font-mono bg-gray-50 p-2 rounded break-all">
                    {selectedDoc.document_id}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    File Name
                  </h4>
                  <p className="text-sm text-docflow-dark break-all">
                    {selectedDoc.file_name}
                  </p>
                </div>
              </div>

              {/* Compact metadata in a grid */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    File Type
                  </h4>
                  <Badge
                    variant="secondary"
                    className={getDocumentTypeColor(selectedDoc.file_type)}
                  >
                    {selectedDoc.file_type.toUpperCase()}
                  </Badge>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    File Size
                  </h4>
                  <p className="text-sm text-docflow-dark">
                    {formatFileSize(selectedDoc.file_size)}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    Upload Date
                  </h4>
                  <p className="text-sm text-docflow-dark">
                    {new Date(selectedDoc.upload_date).toLocaleDateString()}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-docflow-secondary mb-1">
                    Status
                  </h4>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(selectedDoc.embedding_status)}
                    <span className="text-sm capitalize">
                      {selectedDoc.embedding_status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter className="flex justify-between">
              {selectedDoc.embedding_status === "processed" && (
                <Button
                  variant="default"
                  className="bg-docflow-accent hover:bg-docflow-primary"
                  onClick={() => {
                    handleToggleDocumentSelection(selectedDoc);
                    setSelectedDoc(null);
                  }}
                >
                  {selectedDocIds.includes(selectedDoc.document_id)
                    ? "Remove from Query"
                    : "Use for Query"}
                </Button>
              )}
              <Button variant="outline" onClick={() => setSelectedDoc(null)}>
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default DocumentList;
